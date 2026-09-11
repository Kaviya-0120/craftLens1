# CraftLens — Backend API

Voice-first AI catalogue & pricing assistant for Indian artisans.  
Stack: Python · FastAPI · Whisper (self-hosted) · Groq (free tier) · FAISS · rembg · CLIP

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Project Structure](#2-project-structure)
3. [Environment Variables](#3-environment-variables)
4. [Phase 1 — Voice → Transcript → Structured Listing](#4-phase-1--voice--transcript--structured-listing)
   - [Health check](#40-health-check)
   - [POST /voice/transcribe](#41-post-voicetranscribe)
   - [POST /voice/extract-fields](#42-post-voiceextract-fields)
   - [POST /listing/generate](#43-post-listinggenerate)
5. [Phase 2 — Active-learning follow-up loop](#5-phase-2--active-learning-follow-up-loop)
   - [POST /voice/next-question](#51-post-voicenext-question)
6. [End-to-end pipeline script](#6-end-to-end-pipeline-script)
7. [Running tests in isolation](#7-running-tests-in-isolation)
8. [Coming next (Phases 3–7)](#8-coming-next-phases-37)

---

## 1. Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure secrets
cp .env.example .env
# → open .env and fill in GROQ_API_KEY (free at https://console.groq.com/)

# 4. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server is live at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

> **First startup note:** Whisper downloads the `base` model (~145 MB) on the
> first run. This is a one-time download; subsequent starts are fast.
> Set `WHISPER_MODEL=small` in `.env` for better accuracy at the cost of ~465 MB RAM.

---

## 2. Project Structure

```
Craft Lens/
├── app/
│   ├── main.py                  # FastAPI app, CORS, lifespan, router registration
│   ├── routers/
│   │   ├── voice.py             # /voice/* endpoints
│   │   └── listing.py           # /listing/* endpoints
│   ├── services/
│   │   ├── transcription.py     # Whisper wrapper (lazy-loaded singleton)
│   │   ├── llm_client.py        # Provider-agnostic LLM wrapper (Groq default)
│   │   ├── field_extraction.py  # Transcript → structured JSON fields
│   │   ├── listing_generation.py# Fields + transcript → bilingual copy
│   │   └── followup.py          # Confidence-weighted follow-up question
│   ├── models/
│   │   ├── voice.py             # Pydantic schemas for voice pipeline
│   │   ├── listing.py           # Pydantic schemas for listing generation
│   │   └── common.py            # ErrorResponse, HealthResponse
│   └── utils/
│       ├── config.py            # pydantic-settings (reads .env)
│       └── json_parser.py       # Robust JSON extractor for LLM output
├── static/                      # Processed images served here
├── requirements.txt
├── .env.example
└── README.md
```

Each service function is **independently callable** — import and call them
directly in a REPL or unit test without starting the HTTP server.

---

## 3. Environment Variables

Copy `.env.example` to `.env` and fill in values.  
Full list with descriptions is in `.env.example`.

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | **Yes** | — | Free at console.groq.com |
| `LLM_MODEL` | No | `llama3-8b-8192` | Any Groq-hosted model |
| `WHISPER_MODEL` | No | `base` | tiny / base / small / medium |
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./craftlens.db` | SQLite for local dev |

---

## 4. Phase 1 — Voice → Transcript → Structured Listing

Test each endpoint individually before running the full pipeline.

### 4.0 Health check

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

Expected response:
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

### 4.1 POST /voice/transcribe

Upload an audio file. Whisper transcribes it and detects the language.

```bash
curl -s -X POST http://localhost:8000/voice/transcribe \
  -F "file=@/path/to/your/audio.wav" \
  | python3 -m json.tool
```

**Accepted formats:** webm, mp3, wav, ogg, mp4 audio  
**Sample with a test file you can create:**

```bash
# Record a 5-second clip with ffmpeg (needs ffmpeg installed)
ffmpeg -f avfoundation -i ":0" -t 5 test_audio.wav

# Then transcribe
curl -s -X POST http://localhost:8000/voice/transcribe \
  -F "file=@test_audio.wav" \
  | python3 -m json.tool
```

**Success response:**
```json
{
  "transcript": "यह एक बनारसी सिल्क साड़ी है, जिसमें सोने का जरी काम है।",
  "detected_language": "hi"
}
```

**Error response (500):**
```json
{
  "error": "internal_server_error",
  "detail": "Transcription failed: <reason>"
}
```

---

### 4.2 POST /voice/extract-fields

Pass the transcript + language from the previous step. Returns structured
craft metadata with per-field confidence scores.

```bash
curl -s -X POST http://localhost:8000/voice/extract-fields \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "यह एक बनारसी सिल्क साड़ी है, जिसमें सोने का जरी काम है। साइज़ छह मीटर है और कीमत लगभग पाँच हज़ार रुपये है।",
    "detected_language": "hi"
  }' \
  | python3 -m json.tool
```

**Success response:**
```json
{
  "material": "सिल्क",
  "craft_technique": "जरी काम",
  "size": "छह मीटर",
  "region": "बनारस",
  "color": null,
  "price_hint": "पाँच हज़ार रुपये",
  "confidence_per_field": {
    "material": 0.95,
    "craft_technique": 0.9,
    "size": 0.85,
    "region": 0.9
  }
}
```

**English transcript example:**
```bash
curl -s -X POST http://localhost:8000/voice/extract-fields \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "This is a handwoven Kanjivaram silk saree with gold zari border from Tamil Nadu. It is about six yards long.",
    "detected_language": "en"
  }' \
  | python3 -m json.tool
```

---

### 4.3 POST /listing/generate

Takes the structured fields + original transcript, returns bilingual
SEO-ready listing copy (title + description in regional language and English).

```bash
curl -s -X POST http://localhost:8000/listing/generate \
  -H "Content-Type: application/json" \
  -d '{
    "structured_fields": {
      "material": "silk",
      "craft_technique": "zari embroidery",
      "size": "6 yards",
      "region": "Varanasi",
      "color": "red and gold",
      "price_hint": "five thousand rupees",
      "confidence_per_field": {
        "material": 0.95,
        "craft_technique": 0.9,
        "size": 0.85,
        "region": 0.9
      }
    },
    "transcript": "This is a Banarasi silk saree with gold zari work. Six yards long. Around five thousand rupees."
  }' \
  | python3 -m json.tool
```

**Success response:**
```json
{
  "title_regional": "बनारसी सिल्क साड़ी — सोने की जरी कढ़ाई",
  "title_english": "Handcrafted Banarasi Silk Saree with Gold Zari Embroidery | Varanasi",
  "description_regional": "यह खूबसूरत बनारसी साड़ी ...",
  "description_english": "Elevate your wardrobe with this authentic Banarasi silk saree ..."
}
```

---

## 5. Phase 2 — Active-learning follow-up loop

### 5.1 POST /voice/next-question

Identifies the weakest-confidence field that affects pricing and asks
exactly one follow-up question in the artisan's language.

```bash
curl -s -X POST http://localhost:8000/voice/next-question \
  -H "Content-Type: application/json" \
  -d '{
    "structured_fields": {
      "material": "silk",
      "craft_technique": null,
      "size": "6 yards",
      "region": "Varanasi",
      "color": "red",
      "price_hint": null,
      "confidence_per_field": {
        "material": 0.9,
        "craft_technique": 0.1,
        "size": 0.8,
        "region": 0.85
      }
    },
    "detected_language": "hi"
  }' \
  | python3 -m json.tool
```

**Response — follow-up needed:**
```json
{
  "needs_followup": true,
  "field": "craft_technique",
  "question_text": "आपकी साड़ी में कौन सी बुनाई तकनीक इस्तेमाल की गई है — जैसे कटान, जामदानी, या कोई और?",
  "language": "hi"
}
```

**Response — all fields confident:**
```json
{
  "needs_followup": false,
  "field": null,
  "question_text": null,
  "language": null
}
```

**Active-learning loop pattern:**
```
1. POST /voice/transcribe         → transcript, language
2. POST /voice/extract-fields     → fields, confidence
3. POST /voice/next-question      → question (or done)
4. Artisan answers by voice
5. POST /voice/transcribe         → new transcript
6. POST /voice/extract-fields     → updated fields (pass combined transcript)
7. GOTO 3
```

---

## 6. End-to-end pipeline script

Save as `test_pipeline.sh` and run with `bash test_pipeline.sh /path/to/audio.wav`:

```bash
#!/usr/bin/env bash
set -e

BASE="http://localhost:8000"
AUDIO="${1:-test_audio.wav}"

echo "=== Phase 1.1 — Transcribe ==="
TRANSCRIBE=$(curl -s -X POST "$BASE/voice/transcribe" \
  -F "file=@$AUDIO")
echo "$TRANSCRIBE" | python3 -m json.tool

TRANSCRIPT=$(echo "$TRANSCRIBE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['transcript'])")
LANGUAGE=$(echo  "$TRANSCRIBE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['detected_language'])")

echo ""
echo "=== Phase 1.2 — Extract Fields ==="
FIELDS=$(curl -s -X POST "$BASE/voice/extract-fields" \
  -H "Content-Type: application/json" \
  -d "{\"transcript\": $(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$TRANSCRIPT"), \"detected_language\": \"$LANGUAGE\"}")
echo "$FIELDS" | python3 -m json.tool

echo ""
echo "=== Phase 1.3 — Generate Listing ==="
curl -s -X POST "$BASE/listing/generate" \
  -H "Content-Type: application/json" \
  -d "{\"structured_fields\": $FIELDS, \"transcript\": $(python3 -c "import json,sys; print(json.dumps(sys.argv[1]))" "$TRANSCRIPT")}" \
  | python3 -m json.tool

echo ""
echo "=== Phase 2 — Next Question ==="
curl -s -X POST "$BASE/voice/next-question" \
  -H "Content-Type: application/json" \
  -d "{\"structured_fields\": $FIELDS, \"detected_language\": \"$LANGUAGE\"}" \
  | python3 -m json.tool

echo ""
echo "Pipeline complete."
```

---

## 7. Running tests in isolation

Each service function can be called directly without HTTP overhead:

```python
# In a Python REPL or script, from the project root:
import asyncio
from app.services.field_extraction import extract_fields

result = asyncio.run(extract_fields(
    transcript="This is a block-printed cotton kurta from Jaipur, about 42 inches long.",
    detected_language="en"
))
print(result)
```

```python
from app.services.transcription import transcribe_audio

with open("test_audio.wav", "rb") as f:
    audio_bytes = f.read()

result = asyncio.run(transcribe_audio(audio_bytes, "test_audio.wav"))
print(result)
```

---

## 8. Coming next (Phases 3–7)

| Phase | Endpoints | Status |
|---|---|---|
| **3** — Image pipeline | `POST /image/process` (rembg + CLAHE) | Pending |
| **4** — Pricing engine | `POST /pricing/estimate` (FAISS similarity) | Pending |
| **5** — Cross-modal check | `POST /image/tag`, `POST /consistency/check` (CLIP) | Pending |
| **6** — Explainable pricing | `POST /pricing/explain`, `POST /pricing/contest` | Pending |
| **7** — Catalogue publish | `POST /catalogue/publish` (SQLite + QR stub) | Pending |

---

## Notes

- **No paid APIs required for Phase 1.** Whisper runs fully local. Groq has a
  generous free tier (no credit card needed).
- **Swap the LLM:** Set `LLM_PROVIDER` and `LLM_MODEL` in `.env`. Adding
  Gemini support = one new branch in `app/services/llm_client.py`.
- **Swap the Whisper model:** Set `WHISPER_MODEL=small` (or `medium`) in `.env`
  for better multilingual accuracy. No code changes needed.
- **CORS** is wide open (`*`) for local development. Restrict
  `allow_origins` in `app/main.py` before any public deployment.
