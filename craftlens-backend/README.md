# CraftLens — Backend API

Voice-first AI catalogue & pricing assistant for Indian artisans.  
Hackathon MVP · Open Innovation · Ministry of Social Justice and Empowerment

**Stack:** Python 3.11 · FastAPI · Whisper · Groq · rembg · CLIP · FAISS · SQLite  
**No paid APIs required** — Groq has a free tier (no card), Whisper runs fully local.

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Project Structure](#2-project-structure)
3. [Environment Variables](#3-environment-variables)
4. [Swapping Providers](#4-swapping-providers)
5. [Manual Setup — Price Index](#5-manual-setup--price-index)
6. [API Reference with curl Examples](#6-api-reference-with-curl-examples)
   - [Health](#60-health)
   - [Phase 1 — Voice Transcription & Field Extraction](#phase-1--voice-transcription--field-extraction)
   - [Phase 2 — Active-Learning Follow-up](#phase-2--active-learning-follow-up)
   - [Phase 3 — Image Pipeline](#phase-3--image-pipeline)
   - [Phase 4 — Listing Generation](#phase-4--listing-generation)
   - [Phase 5 — Pricing Estimate](#phase-5--pricing-estimate)
   - [Phase 6 — Cross-Modal Consistency](#phase-6--cross-modal-consistency)
   - [Phase 7 — Explainable & Contestable Pricing](#phase-7--explainable--contestable-pricing)
   - [Phase 8 — Catalogue Publish](#phase-8--catalogue-publish)
7. [Running the Smoke Test Suite](#7-running-the-smoke-test-suite)

---

## 1. Quick Start

```bash
# Clone / open the project
cd craftlens-backend

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies (~5 min first time; PyTorch is the heavy one)
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
# Open .env and set GROQ_API_KEY (free at https://console.groq.com/ — no card needed)

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server is live at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

> **First startup:** Whisper downloads the `base` model (~145 MB) once. Subsequent starts are instant.  
> Set `WHISPER_MODEL_SIZE=small` in `.env` for better multilingual accuracy (~465 MB).

---

## 2. Project Structure

```
craftlens-backend/
├── app/
│   ├── main.py                     FastAPI app, CORS, lifespan, all routers
│   ├── config.py                   pydantic-settings singleton (reads .env)
│   ├── routers/
│   │   ├── voice.py                /voice/* — transcribe, extract-fields, next-question
│   │   ├── image.py                /image/* — process, tag
│   │   ├── listing.py              /listing/generate
│   │   ├── pricing.py              /pricing/* — estimate, explain, contest
│   │   ├── consistency.py          /consistency/check
│   │   └── catalogue.py            /catalogue/publish  +  GET /listing/{id}
│   ├── services/
│   │   ├── asr_service.py          Whisper + Bhashini (swappable via ASR_PROVIDER)
│   │   ├── llm_service.py          Groq / Gemini / Ollama (swappable via LLM_PROVIDER)
│   │   ├── image_service.py        rembg background removal + OpenCV CLAHE
│   │   ├── clip_service.py         open_clip ViT-B-32 zero-shot tagging
│   │   ├── pricing_service.py      FAISS similarity search + price stats
│   │   └── db_service.py           SQLAlchemy SQLite persistence
│   ├── models/
│   │   └── schemas.py              All Pydantic request/response models
│   ├── prompts/
│   │   ├── field_extraction.txt
│   │   ├── followup_question.txt
│   │   ├── listing_generation.txt
│   │   ├── pricing_explanation.txt
│   │   └── consistency_question.txt
│   └── utils/
│       └── errors.py               Standard error response helpers
├── data/                           Place Kaggle CSV here (see §5)
├── scripts/
│   └── build_price_index.py        One-time: CSV → embeddings → FAISS index
├── static/                         Processed images saved here
├── tests/
│   └── test_endpoints.sh           curl smoke test for every endpoint
├── requirements.txt
├── .env.example
└── README.md
```

---

## 3. Environment Variables

Copy `.env.example` to `.env`. Full descriptions are in the example file.

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | `groq` \| `gemini` \| `ollama` |
| `GROQ_API_KEY` | — | **Required for Groq.** Free at console.groq.com |
| `GROQ_MODEL` | `llama3-8b-8192` | Any Groq-hosted model |
| `GEMINI_API_KEY` | — | Required if `LLM_PROVIDER=gemini` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Required if `LLM_PROVIDER=ollama` |
| `ASR_PROVIDER` | `whisper` | `whisper` \| `bhashini` |
| `WHISPER_MODEL_SIZE` | `base` | `tiny` / `base` / `small` / `medium` |
| `BHASHINI_API_KEY` | — | Required if `ASR_PROVIDER=bhashini` |
| `PRICE_INDEX_PATH` | `./data/price_index.faiss` | Output of build script |
| `PRICE_METADATA_PATH` | `./data/price_metadata.csv` | Output of build script |
| `DATABASE_URL` | `sqlite:///./craftlens.db` | SQLite for local dev |
| `CONFIDENCE_THRESHOLD` | `0.7` | Follow-up trigger threshold |
| `CONSISTENCY_THRESHOLD` | `0.4` | CLIP vs voice mismatch threshold |

---

## 4. Swapping Providers

**Switch LLM backend** — edit `.env`, no code changes:
```
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

**Switch ASR backend:**
```
ASR_PROVIDER=bhashini
BHASHINI_API_KEY=your_key
BHASHINI_USER_ID=your_user_id
BHASHINI_PIPELINE_ID=your_pipeline_id
```

**Use a larger Whisper model** for better accuracy on regional languages:
```
WHISPER_MODEL_SIZE=small
```

---

## 5. Manual Setup — Price Index

The pricing engine requires a one-time index build from a Kaggle product dataset.

**Step 1 — Download dataset:**
- Go to Kaggle and download one of:
  - [Flipkart Products](https://www.kaggle.com/datasets/PromptCloudHQ/flipkart-products) (`flipkart_com-ecommerce_sample.csv`)
  - [Amazon India Products](https://www.kaggle.com/datasets/lokeshparab/amazon-products-dataset)
- Place the CSV file in `./data/`

**Step 2 — Build the index:**
```bash
python scripts/build_price_index.py
```

This creates `./data/price_index.faiss` and `./data/price_metadata.csv`.  
Runtime: ~5–15 min on CPU for a ~15k-row dataset.

**Step 3 — Verify:**
```bash
python -c "import faiss; idx = faiss.read_index('./data/price_index.faiss'); print('Vectors:', idx.ntotal)"
```

---

## 6. API Reference with curl Examples

All examples assume the server is running on `http://localhost:8000`.

### 6.0 Health

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```
```json
{ "status": "ok" }
```

---

### Phase 1 — Voice Transcription & Field Extraction

#### POST /voice/transcribe

```bash
curl -s -X POST http://localhost:8000/voice/transcribe \
  -F "file=@/path/to/your/audio.wav" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "transcript": "यह एक बनारसी सिल्क साड़ी है, सोने का जरी काम है, छह मीटर लंबी।",
  "detected_language": "hi",
  "confidence": 1.0
}
```

**Test with a quick recording (needs ffmpeg):**
```bash
# Record 5 seconds from microphone
ffmpeg -f avfoundation -i ":0" -t 5 /tmp/test_craft.wav

curl -s -X POST http://localhost:8000/voice/transcribe \
  -F "file=@/tmp/test_craft.wav" \
  | python3 -m json.tool
```

#### POST /voice/extract-fields

```bash
curl -s -X POST http://localhost:8000/voice/extract-fields \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "This is a handwoven Banarasi silk saree with gold zari embroidery from Varanasi. Six yards long. Around five thousand rupees.",
    "language": "en"
  }' \
  | python3 -m json.tool
```

Expected response:
```json
{
  "fields": {
    "material": "silk",
    "craft_technique": "zari embroidery",
    "size": "6 yards",
    "region": "Varanasi",
    "color": null,
    "price_hint": 5000
  },
  "confidence": {
    "material": 0.95,
    "craft_technique": 0.9,
    "size": 0.85,
    "region": 0.9
  },
  "transcript_used": "This is a handwoven Banarasi silk saree..."
}
```

**With previous transcript (multi-turn loop):**
```bash
curl -s -X POST http://localhost:8000/voice/extract-fields \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "The technique is Katan weave, not plain weave.",
    "language": "en",
    "previous_transcript": "This is a Banarasi silk saree from Varanasi."
  }' \
  | python3 -m json.tool
```

---

### Phase 2 — Active-Learning Follow-up

#### POST /voice/next-question

```bash
curl -s -X POST http://localhost:8000/voice/next-question \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "material": "silk",
      "craft_technique": null,
      "size": "6 yards",
      "region": "Varanasi",
      "color": null,
      "price_hint": null
    },
    "confidence": {
      "material": 0.9,
      "craft_technique": 0.1,
      "size": 0.8,
      "region": 0.85
    },
    "language": "hi"
  }' \
  | python3 -m json.tool
```

Expected response (follow-up needed):
```json
{
  "needs_followup": true,
  "field": "craft_technique",
  "question_text": "आपकी साड़ी में कौन सी बुनाई तकनीक है — जैसे कटान, जामदानी, या कोई और?",
  "language": "hi"
}
```

Expected response (all fields confident):
```json
{
  "needs_followup": false,
  "field": null,
  "question_text": null,
  "language": null
}
```

---

### Phase 3 — Image Pipeline

#### POST /image/process

```bash
curl -s -X POST http://localhost:8000/image/process \
  -F "file=@/path/to/product_photo.jpg" \
  | python3 -m json.tool
```

Expected response:
```json
{
  "processed_image_url": "/static/a1b2c3d4-...-.png",
  "image_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

View the processed image:
```bash
# Open in browser or download
curl -s "http://localhost:8000/static/<image_id>.png" --output processed.png
```

> **Note on first run:** rembg will download `isnet-general-use` model weights (~170 MB). The log will show "downloading model weights" — this is expected and happens only once.

---

### Phase 4 — Listing Generation

#### POST /listing/generate

```bash
curl -s -X POST http://localhost:8000/listing/generate \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "material": "silk",
      "craft_technique": "zari embroidery",
      "size": "6 yards",
      "region": "Varanasi",
      "color": "red and gold",
      "price_hint": 5000
    },
    "transcript_original_language": "यह एक बनारसी सिल्क साड़ी है, सोने का जरी काम है।",
    "language": "hi"
  }' \
  | python3 -m json.tool
```

Expected response:
```json
{
  "title_regional": "बनारसी सिल्क साड़ी — असली सोने की जरी",
  "title_english": "Handwoven Banarasi Silk Saree with Gold Zari Embroidery | Varanasi",
  "description_regional": "यह साड़ी वाराणसी के कुशल बुनकरों द्वारा...",
  "description_english": "Drape yourself in heritage with this authentic Banarasi silk saree..."
}
```

---

### Phase 5 — Pricing Estimate

> **Requires the price index to be built first** (see §5).

#### POST /pricing/estimate

```bash
curl -s -X POST http://localhost:8000/pricing/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "material": "silk",
      "craft_technique": "zari embroidery",
      "size": "6 yards",
      "region": "Varanasi",
      "color": "red",
      "price_hint": null
    },
    "listing_text": "Handwoven Banarasi Silk Saree with Gold Zari Embroidery from Varanasi 6 yards"
  }' \
  | python3 -m json.tool
```

Expected response:
```json
{
  "price_range": [1200.0, 8500.0],
  "median_price": 3499.0,
  "comparable_count": 10,
  "comparable_samples": [
    { "title": "Banarasi Silk Saree Gold Border", "price": 3299.0, "category": "sarees" }
  ],
  "low_confidence": false
}
```

---

### Phase 6 — Cross-Modal Consistency

#### POST /image/tag (requires processed image)

```bash
curl -s -X POST http://localhost:8000/image/tag \
  -H "Content-Type: application/json" \
  -d '{"image_id": "YOUR_IMAGE_ID_FROM_PHASE_3"}' \
  | python3 -m json.tool
```

Expected response:
```json
{
  "visual_tags": [
    { "label": "silk fabric", "score": 0.4821 },
    { "label": "zari embroidery", "score": 0.3104 },
    { "label": "handloom weave", "score": 0.1233 }
  ]
}
```

#### POST /consistency/check

```bash
curl -s -X POST http://localhost:8000/consistency/check \
  -H "Content-Type: application/json" \
  -d '{
    "voice_material": "cotton",
    "voice_craft": "block print",
    "visual_tags": [
      { "label": "silk fabric", "score": 0.52 },
      { "label": "zari embroidery", "score": 0.28 },
      { "label": "handloom weave", "score": 0.12 }
    ],
    "language": "en"
  }' \
  | python3 -m json.tool
```

Expected response (mismatch detected):
```json
{
  "mismatch": true,
  "voice_claim": "cotton block print",
  "closest_visual_tag": "silk fabric",
  "similarity_score": 0.2341,
  "confirmation_question": "You mentioned cotton block print, but the photo looks like it might be silk — can you confirm the material?"
}
```

---

### Phase 7 — Explainable & Contestable Pricing

#### POST /pricing/explain

```bash
curl -s -X POST http://localhost:8000/pricing/explain \
  -H "Content-Type: application/json" \
  -d '{
    "pricing_result": {
      "price_range": [1200.0, 8500.0],
      "median_price": 3499.0,
      "comparable_count": 10,
      "comparable_samples": [],
      "low_confidence": false
    },
    "fields": {
      "material": "silk",
      "craft_technique": "zari embroidery",
      "size": "6 yards",
      "region": "Varanasi",
      "color": "red",
      "price_hint": null
    },
    "language": "en"
  }' \
  | python3 -m json.tool
```

Expected response:
```json
{
  "explanation_text": "Based on 10 similar products on the market, a Banarasi silk saree with real zari embroidery typically sells between ₹1,200 and ₹8,500, with a median of ₹3,499. The real zari work and Varanasi origin are key factors that place it in the higher range.",
  "language": "en"
}
```

#### POST /pricing/contest

```bash
curl -s -X POST http://localhost:8000/pricing/contest \
  -H "Content-Type: application/json" \
  -d '{
    "correction_transcript": "Actually this is pure Katan silk, not regular silk. The zari is real gold thread, not synthetic.",
    "language": "en",
    "original_fields": {
      "material": "silk",
      "craft_technique": "zari embroidery",
      "size": "6 yards",
      "region": "Varanasi",
      "color": "red",
      "price_hint": null
    }
  }' \
  | python3 -m json.tool
```

Expected response:
```json
{
  "updated_fields": {
    "material": "Katan silk",
    "craft_technique": "real gold zari embroidery",
    ...
  },
  "updated_pricing": { "price_range": [3500.0, 12000.0], ... },
  "updated_explanation": "With pure Katan silk and genuine gold zari, comparable products range from ₹3,500 to ₹12,000..."
}
```

---

### Phase 8 — Catalogue Publish

#### POST /catalogue/publish

```bash
curl -s -X POST http://localhost:8000/catalogue/publish \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "/static/a1b2c3d4.png",
    "title_regional": "बनारसी सिल्क साड़ी — असली सोने की जरी",
    "title_english": "Handwoven Banarasi Silk Saree with Gold Zari | Varanasi",
    "description_regional": "यह साड़ी वाराणसी के कुशल बुनकरों द्वारा बनाई गई है।",
    "description_english": "An authentic handwoven Banarasi silk saree with real gold zari.",
    "price": 4500.0,
    "fields": {
      "material": "silk",
      "craft_technique": "zari embroidery",
      "size": "6 yards",
      "region": "Varanasi",
      "color": "red",
      "price_hint": null
    }
  }' \
  | python3 -m json.tool
```

Expected response:
```json
{
  "listing_id": "f1e2d3c4-b5a6-7890-abcd-ef1234567890",
  "share_url": "/listing/f1e2d3c4-b5a6-7890-abcd-ef1234567890"
}
```

#### GET /listing/{id}

```bash
curl -s http://localhost:8000/listing/f1e2d3c4-b5a6-7890-abcd-ef1234567890 \
  | python3 -m json.tool
```

Returns the full stored listing record as JSON — this is the shareable / QR-ready URL.

---

## 7. Running the Smoke Test Suite

```bash
# Basic run (skips transcription and image tests — uses stub data)
./tests/test_endpoints.sh

# Full run with real audio and image files
./tests/test_endpoints.sh /path/to/craft_description.wav /path/to/product_photo.jpg
```

The script runs every endpoint in build order and prints `PASS / FAIL / SKIP` per phase.  
Pricing tests are automatically skipped if the FAISS index hasn't been built yet.

---

## Notes

- **CORS** is wide open (`*`) for local development. Lock down `allow_origins` in `app/main.py` before any public deployment.
- **Error format** — every endpoint returns `{ "error": true, "message": "...", "detail": "..." }` on failure. Raw Python tracebacks are logged server-side only.
- **File size limit** — all uploads capped at 10 MB (configurable via `MAX_UPLOAD_BYTES` in `.env`).
- **LLM JSON robustness** — `/voice/extract-fields` retries once with a stricter prompt if the LLM returns malformed JSON. The `parse_llm_json()` utility also strips markdown fences as a fallback.
