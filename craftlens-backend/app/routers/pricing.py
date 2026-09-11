"""
Pricing Router — Phase 5 & 7

  POST /pricing/estimate    fields + listing text → FAISS price range
  POST /pricing/explain     pricing result + fields → voice-style explanation
  POST /pricing/contest     correction transcript → re-estimate + re-explain
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from app.models.schemas import (
    ComparableSample,
    ExtractedFields,
    FieldConfidence,
    PricingContestRequest,
    PricingContestResponse,
    PricingEstimateRequest,
    PricingEstimateResponse,
    PricingExplainRequest,
    PricingExplainResponse,
)
from app.services import llm_service, pricing_service
from app.utils.errors import craft_error_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pricing", tags=["Pricing Engine"])


# ─────────────────────────────────────────────────────────────────────────────
# POST /pricing/estimate
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/estimate",
    response_model=PricingEstimateResponse,
    summary="Estimate price range via FAISS similarity search",
    description=(
        "Embeds the listing text, searches the pre-built product index, "
        "and returns a price range + median from the top-k matches. "
        "Requires the price index to be built first (see scripts/build_price_index.py)."
    ),
)
async def estimate_price(body: PricingEstimateRequest):
    try:
        result = pricing_service.estimate_price(
            fields=body.fields.model_dump(),
            listing_text=body.listing_text,
        )
        return PricingEstimateResponse(
            price_range=result["price_range"],
            median_price=result["median_price"],
            comparable_count=result["comparable_count"],
            comparable_samples=[
                ComparableSample(**s) for s in result["comparable_samples"]
            ],
            low_confidence=result["low_confidence"],
        )
    except RuntimeError as exc:
        return craft_error_response(500, "Pricing estimation failed.", exc)
    except Exception as exc:
        return craft_error_response(500, "Unexpected error during pricing.", exc)


# ─────────────────────────────────────────────────────────────────────────────
# POST /pricing/explain
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/explain",
    response_model=PricingExplainResponse,
    summary="Generate a voice-style explanation of the price estimate",
    description=(
        "Calls the LLM to produce a natural, grounded explanation citing "
        "the actual price range and comparable count. "
        "The LLM is instructed not to invent numbers."
    ),
)
async def explain_price(body: PricingExplainRequest):
    pricing = body.pricing_result
    fields = body.fields

    system_prompt = llm_service.load_prompt("pricing_explanation")

    # Highlight fields that plausibly affect price
    highlight = [
        f"{k}: {v}"
        for k, v in fields.model_dump().items()
        if v is not None and k not in ("price_hint",)
    ]

    user_prompt = (
        f"Price range: ₹{pricing.price_range[0]:,.0f} – ₹{pricing.price_range[1]:,.0f}\n"
        f"Median price: ₹{pricing.median_price:,.0f}\n"
        f"Comparable products found: {pricing.comparable_count}\n"
        f"Low confidence estimate: {pricing.low_confidence}\n\n"
        f"Product details:\n" + "\n".join(highlight)
    )

    try:
        explanation = llm_service.call_llm(
            system_prompt, user_prompt, json_mode=False
        ).strip()
    except RuntimeError as exc:
        return craft_error_response(500, "LLM call failed.", exc)
    except Exception as exc:
        return craft_error_response(500, "Unexpected error generating explanation.", exc)

    return PricingExplainResponse(
        explanation_text=explanation,
        language=body.language,
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /pricing/contest
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/contest",
    response_model=PricingContestResponse,
    summary="Re-estimate price after artisan correction",
    description=(
        "The artisan speaks a correction. Their new transcript is merged "
        "with original fields, pricing is re-estimated, and a new explanation "
        "is generated."
    ),
)
async def contest_price(body: PricingContestRequest):
    # Step 1 — Re-extract fields using correction transcript + original fields as context
    system_prompt = llm_service.load_prompt("field_extraction")
    original_str = "\n".join(
        f"  {k}: {v}"
        for k, v in body.original_fields.model_dump().items()
        if v is not None
    )
    user_prompt = (
        f"Language: {body.language}\n\n"
        f"Original fields (use as context — the artisan is correcting these):\n{original_str}\n\n"
        f"Correction transcript:\n{body.correction_transcript}"
    )

    try:
        raw = llm_service.call_llm(system_prompt, user_prompt, json_mode=True)
        updated_data = llm_service.parse_llm_json(raw)
    except (ValueError, RuntimeError) as exc:
        return craft_error_response(500, "Field re-extraction failed.", exc)

    # Merge: prefer updated non-null values over originals
    original_dict = body.original_fields.model_dump()
    for k, v in updated_data.items():
        if k in original_dict and v is not None and k != "confidence":
            original_dict[k] = v

    updated_fields = ExtractedFields(**{
        k: original_dict.get(k) for k in ExtractedFields.model_fields
    })

    # Step 2 — Re-estimate price
    listing_text = " ".join(str(v) for v in original_dict.values() if v)
    try:
        price_result = pricing_service.estimate_price(
            fields=updated_fields.model_dump(),
            listing_text=listing_text,
        )
    except RuntimeError as exc:
        return craft_error_response(500, "Pricing re-estimation failed.", exc)

    pricing_response = PricingEstimateResponse(
        price_range=price_result["price_range"],
        median_price=price_result["median_price"],
        comparable_count=price_result["comparable_count"],
        comparable_samples=[ComparableSample(**s) for s in price_result["comparable_samples"]],
        low_confidence=price_result["low_confidence"],
    )

    # Step 3 — Re-generate explanation
    explain_prompt = llm_service.load_prompt("pricing_explanation")
    highlight = [f"{k}: {v}" for k, v in updated_fields.model_dump().items() if v]
    explain_user = (
        f"Price range: ₹{price_result['price_range'][0]:,.0f} – ₹{price_result['price_range'][1]:,.0f}\n"
        f"Median price: ₹{price_result['median_price']:,.0f}\n"
        f"Comparable products found: {price_result['comparable_count']}\n\n"
        f"Product details:\n" + "\n".join(highlight)
    )

    try:
        explanation = llm_service.call_llm(explain_prompt, explain_user, json_mode=False).strip()
    except RuntimeError as exc:
        return craft_error_response(500, "Explanation generation failed.", exc)

    return PricingContestResponse(
        updated_fields=updated_fields,
        updated_pricing=pricing_response,
        updated_explanation=explanation,
    )
