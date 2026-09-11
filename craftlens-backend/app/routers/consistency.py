"""
Consistency Router — Phase 6 (Novelty 2)

  POST /consistency/check   voice claims vs CLIP visual tags → mismatch detection
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from app.models.schemas import ConsistencyCheckRequest, ConsistencyCheckResponse
from app.services import llm_service
from app.utils.errors import craft_error_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/consistency", tags=["Cross-Modal Consistency"])


@router.post(
    "/check",
    response_model=ConsistencyCheckResponse,
    summary="Check voice-claimed material against CLIP visual tags",
    description=(
        "Computes semantic similarity between the voice-extracted material/craft "
        "and the top CLIP visual tag. If below threshold, generates a spoken "
        "confirmation question in the artisan's language."
    ),
)
async def check_consistency(body: ConsistencyCheckRequest):
    # Build the voice claim string
    voice_claim = " ".join(
        filter(None, [body.voice_material, body.voice_craft])
    ).strip()

    if not body.visual_tags:
        return craft_error_response(400, "visual_tags list is empty — run /image/tag first.")

    top_visual = body.visual_tags[0]
    closest_label = top_visual.label

    # Semantic similarity using sentence-transformers (same model as pricing, no extra cost)
    try:
        from sentence_transformers import SentenceTransformer, util  # type: ignore
        from app.config import settings

        model = SentenceTransformer(settings.embedding_model)
        emb_voice = model.encode(voice_claim, convert_to_tensor=True)
        emb_visual = model.encode(closest_label, convert_to_tensor=True)
        sim_score = float(util.cos_sim(emb_voice, emb_visual)[0][0])
    except Exception as exc:
        return craft_error_response(500, "Similarity computation failed.", exc)

    from app.config import settings as cfg
    threshold = cfg.consistency_threshold
    mismatch = sim_score < threshold

    confirmation_question = None
    if mismatch:
        system_prompt = llm_service.load_prompt("consistency_question")
        user_prompt = (
            f"Language: {body.language}\n"
            f"Artisan's claim: {voice_claim}\n"
            f"What the photo suggests: {closest_label}\n"
            f"Similarity score: {sim_score:.2f} (below threshold {threshold})"
        )
        try:
            confirmation_question = llm_service.call_llm(
                system_prompt, user_prompt, json_mode=False
            ).strip()
        except RuntimeError as exc:
            return craft_error_response(500, "LLM call for consistency question failed.", exc)

    return ConsistencyCheckResponse(
        mismatch=mismatch,
        voice_claim=voice_claim,
        closest_visual_tag=closest_label,
        similarity_score=round(sim_score, 4),
        confirmation_question=confirmation_question,
    )
