#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# CraftLens — End-to-end smoke test (curl)
# Tests every endpoint in build order against a running local server.
#
# Usage:
#   chmod +x tests/test_endpoints.sh
#   ./tests/test_endpoints.sh [path/to/audio.wav] [path/to/image.jpg]
#
# Requirements:
#   - Server running: uvicorn app.main:app --reload --port 8000
#   - jq installed: brew install jq  /  apt install jq
#   - Optionally provide an audio file and an image file as args
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

BASE="http://localhost:8000"
AUDIO="${1:-}"
IMAGE="${2:-}"

PASS=0
FAIL=0

# ── Colour helpers ────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}  ✓ PASS${NC} — $1"; PASS=$((PASS+1)); }
fail() { echo -e "${RED}  ✗ FAIL${NC} — $1"; FAIL=$((FAIL+1)); }
skip() { echo -e "${YELLOW}  ⊘ SKIP${NC} — $1"; }
header() { echo -e "\n${YELLOW}══ $1 ══${NC}"; }

# Checks that a response contains a given JSON key
check_key() {
  local label="$1" response="$2" key="$3"
  if echo "$response" | jq -e ".$key" > /dev/null 2>&1; then
    pass "$label — has '$key'"
  else
    fail "$label — missing '$key'"
    echo "    Response: $response" | head -c 500
  fi
}

# ─────────────────────────────────────────────────────────────
header "SYSTEM — /health"
RESP=$(curl -s "$BASE/health")
check_key "/health" "$RESP" "status"

# ─────────────────────────────────────────────────────────────
header "PHASE 1 — Voice Transcription"

if [ -z "$AUDIO" ]; then
  skip "/voice/transcribe — no audio file provided (pass as first arg)"
  # Use a stub transcript for downstream tests
  TRANSCRIPT="This is a handwoven Banarasi silk saree with gold zari embroidery from Varanasi. It is six yards long. The price is around five thousand rupees."
  LANGUAGE="en"
  echo "    Using stub transcript for downstream tests."
else
  echo "  Testing /voice/transcribe with: $AUDIO"
  RESP=$(curl -s -X POST "$BASE/voice/transcribe" -F "file=@$AUDIO")
  check_key "/voice/transcribe" "$RESP" "transcript"
  check_key "/voice/transcribe" "$RESP" "detected_language"
  TRANSCRIPT=$(echo "$RESP" | jq -r '.transcript // "stub transcript"')
  LANGUAGE=$(echo  "$RESP" | jq -r '.detected_language // "en"')
fi

echo "  Transcript: ${TRANSCRIPT:0:80}…"
echo "  Language:   $LANGUAGE"

# ─────────────────────────────────────────────────────────────
header "PHASE 1 — Field Extraction"

FIELDS_RESP=$(curl -s -X POST "$BASE/voice/extract-fields" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc --arg t "$TRANSCRIPT" --arg l "$LANGUAGE" \
    '{transcript: $t, language: $l}')")

check_key "/voice/extract-fields" "$FIELDS_RESP" "fields"
check_key "/voice/extract-fields" "$FIELDS_RESP" "confidence"
check_key "/voice/extract-fields" "$FIELDS_RESP" "transcript_used"

FIELDS_JSON=$(echo "$FIELDS_RESP" | jq '.fields')
CONFIDENCE_JSON=$(echo "$FIELDS_RESP" | jq '.confidence')
echo "  Fields:     $FIELDS_JSON"
echo "  Confidence: $CONFIDENCE_JSON"

# ─────────────────────────────────────────────────────────────
header "PHASE 2 — Follow-up Question"

NQ_RESP=$(curl -s -X POST "$BASE/voice/next-question" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc \
    --argjson f "$FIELDS_JSON" \
    --argjson c "$CONFIDENCE_JSON" \
    --arg l "$LANGUAGE" \
    '{fields: $f, confidence: $c, language: $l}')")

check_key "/voice/next-question" "$NQ_RESP" "needs_followup"
echo "  needs_followup: $(echo $NQ_RESP | jq '.needs_followup')"
echo "  question_text:  $(echo $NQ_RESP | jq -r '.question_text // "(none needed)"')"

# ─────────────────────────────────────────────────────────────
header "PHASE 3 — Image Processing"

if [ -z "$IMAGE" ]; then
  skip "/image/process — no image file provided (pass as second arg)"
  IMAGE_ID=""
else
  echo "  Testing /image/process with: $IMAGE"
  IMG_RESP=$(curl -s -X POST "$BASE/image/process" -F "file=@$IMAGE")
  check_key "/image/process" "$IMG_RESP" "image_id"
  check_key "/image/process" "$IMG_RESP" "processed_image_url"
  IMAGE_ID=$(echo "$IMG_RESP" | jq -r '.image_id // ""')
  echo "  image_id: $IMAGE_ID"

  if [ -n "$IMAGE_ID" ]; then
    header "PHASE 6a — CLIP Tagging"
    TAG_RESP=$(curl -s -X POST "$BASE/image/tag" \
      -H "Content-Type: application/json" \
      -d "{\"image_id\": \"$IMAGE_ID\"}")
    check_key "/image/tag" "$TAG_RESP" "visual_tags"
    VISUAL_TAGS=$(echo "$TAG_RESP" | jq '.visual_tags')
    echo "  visual_tags: $VISUAL_TAGS"

    header "PHASE 6b — Consistency Check"
    VOICE_MATERIAL=$(echo "$FIELDS_JSON" | jq -r '.material // "silk"')
    VOICE_CRAFT=$(echo "$FIELDS_JSON" | jq -r '.craft_technique // "zari embroidery"')
    CC_RESP=$(curl -s -X POST "$BASE/consistency/check" \
      -H "Content-Type: application/json" \
      -d "$(jq -nc \
        --arg vm "$VOICE_MATERIAL" \
        --arg vc "$VOICE_CRAFT" \
        --argjson vt "$VISUAL_TAGS" \
        --arg lang "$LANGUAGE" \
        '{voice_material: $vm, voice_craft: $vc, visual_tags: $vt, language: $lang}')")
    check_key "/consistency/check" "$CC_RESP" "mismatch"
    echo "  mismatch: $(echo $CC_RESP | jq '.mismatch')"
    echo "  similarity_score: $(echo $CC_RESP | jq '.similarity_score')"
  fi
fi

# ─────────────────────────────────────────────────────────────
header "PHASE 4 — Listing Generation"

LISTING_RESP=$(curl -s -X POST "$BASE/listing/generate" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc \
    --argjson f "$FIELDS_JSON" \
    --arg t "$TRANSCRIPT" \
    --arg l "$LANGUAGE" \
    '{fields: $f, transcript_original_language: $t, language: $l}')")

check_key "/listing/generate" "$LISTING_RESP" "title_english"
check_key "/listing/generate" "$LISTING_RESP" "title_regional"
check_key "/listing/generate" "$LISTING_RESP" "description_english"
check_key "/listing/generate" "$LISTING_RESP" "description_regional"

TITLE_EN=$(echo "$LISTING_RESP" | jq -r '.title_english // ""')
echo "  title_english: $TITLE_EN"

# ─────────────────────────────────────────────────────────────
header "PHASE 5 — Pricing Estimate"

PRICE_RESP=$(curl -s -X POST "$BASE/pricing/estimate" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc \
    --argjson f "$FIELDS_JSON" \
    --arg lt "$TITLE_EN $TRANSCRIPT" \
    '{fields: $f, listing_text: $lt}')")

# Pricing may fail if index not built — show warning, don't hard-fail the suite
if echo "$PRICE_RESP" | jq -e '.error' > /dev/null 2>&1; then
  skip "/pricing/estimate — index not built yet (run scripts/build_price_index.py)"
  echo "    Error: $(echo $PRICE_RESP | jq -r '.message')"
  # Use a stub for downstream pricing tests
  PRICE_RESP='{"price_range":[500,5000],"median_price":2500,"comparable_count":5,"comparable_samples":[],"low_confidence":true}'
else
  check_key "/pricing/estimate" "$PRICE_RESP" "price_range"
  check_key "/pricing/estimate" "$PRICE_RESP" "median_price"
  echo "  price_range:  $(echo $PRICE_RESP | jq '.price_range')"
  echo "  median_price: $(echo $PRICE_RESP | jq '.median_price')"
fi

# ─────────────────────────────────────────────────────────────
header "PHASE 7 — Pricing Explanation"

EXPLAIN_RESP=$(curl -s -X POST "$BASE/pricing/explain" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc \
    --argjson pr "$PRICE_RESP" \
    --argjson f "$FIELDS_JSON" \
    --arg l "$LANGUAGE" \
    '{pricing_result: $pr, fields: $f, language: $l}')")

check_key "/pricing/explain" "$EXPLAIN_RESP" "explanation_text"
echo "  explanation: $(echo $EXPLAIN_RESP | jq -r '.explanation_text // ""' | head -c 200)…"

# ─────────────────────────────────────────────────────────────
header "PHASE 7 — Pricing Contest"

CONTEST_RESP=$(curl -s -X POST "$BASE/pricing/contest" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc \
    --arg ct "Actually it is pure Katan silk, not regular silk, and the zari is real gold." \
    --arg l "$LANGUAGE" \
    --argjson of "$FIELDS_JSON" \
    '{correction_transcript: $ct, language: $l, original_fields: $of}')")

if echo "$CONTEST_RESP" | jq -e '.error' > /dev/null 2>&1; then
  skip "/pricing/contest — skipped (pricing index not built)"
else
  check_key "/pricing/contest" "$CONTEST_RESP" "updated_fields"
  check_key "/pricing/contest" "$CONTEST_RESP" "updated_pricing"
  check_key "/pricing/contest" "$CONTEST_RESP" "updated_explanation"
fi

# ─────────────────────────────────────────────────────────────
header "PHASE 8 — Catalogue Publish"

IMG_URL="${IMAGE_ID:+/static/$IMAGE_ID.png}"
IMG_URL="${IMG_URL:-/static/placeholder.png}"

PUB_RESP=$(curl -s -X POST "$BASE/catalogue/publish" \
  -H "Content-Type: application/json" \
  -d "$(jq -nc \
    --arg iu "$IMG_URL" \
    --arg tr "$(echo $LISTING_RESP | jq -r '.title_regional // "शीर्षक"')" \
    --arg te "$(echo $LISTING_RESP | jq -r '.title_english // "Title"')" \
    --arg dr "$(echo $LISTING_RESP | jq -r '.description_regional // "विवरण"')" \
    --arg de "$(echo $LISTING_RESP | jq -r '.description_english // "Description"')" \
    --argjson f "$FIELDS_JSON" \
    '{image_url: $iu, title_regional: $tr, title_english: $te,
      description_regional: $dr, description_english: $de,
      price: 3500, fields: $f}')")

check_key "/catalogue/publish" "$PUB_RESP" "listing_id"
check_key "/catalogue/publish" "$PUB_RESP" "share_url"

LISTING_ID=$(echo "$PUB_RESP" | jq -r '.listing_id // ""')
echo "  listing_id: $LISTING_ID"

if [ -n "$LISTING_ID" ]; then
  header "PHASE 8 — GET /listing/{id}"
  GET_RESP=$(curl -s "$BASE/listing/$LISTING_ID")
  check_key "GET /listing/{id}" "$GET_RESP" "id"
  check_key "GET /listing/{id}" "$GET_RESP" "title_english"
  check_key "GET /listing/{id}" "$GET_RESP" "price"
fi

# ─────────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
echo -e "Results: ${GREEN}$PASS passed${NC}  |  ${RED}$FAIL failed${NC}"
echo "═══════════════════════════════════════════"

[ "$FAIL" -eq 0 ]
