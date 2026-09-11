import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({ baseURL: API_BASE_URL })

// ── Voice ──────────────────────────────────────────────────────
export const transcribeAudio = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/voice/transcribe', fd)
}

export const extractFields = (transcript, language, previousTranscript = null) =>
  api.post('/voice/extract-fields', {
    transcript,
    language,
    ...(previousTranscript ? { previous_transcript: previousTranscript } : {}),
  })

export const nextQuestion = (fields, confidence, language) =>
  api.post('/voice/next-question', { fields, confidence, language })

// ── Image ──────────────────────────────────────────────────────
export const processImage = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/image/process', fd)
}

export const tagImage = (imageId) =>
  api.post('/image/tag', { image_id: imageId })

// ── Listing ────────────────────────────────────────────────────
export const generateListing = (fields, transcriptOriginal, language) =>
  api.post('/listing/generate', {
    fields,
    transcript_original_language: transcriptOriginal,
    language,
  })

// ── Pricing ────────────────────────────────────────────────────
export const estimatePrice = (fields, listingText) =>
  api.post('/pricing/estimate', { fields, listing_text: listingText })

export const explainPrice = (pricingResult, fields, language) =>
  api.post('/pricing/explain', { pricing_result: pricingResult, fields, language })

export const contestPrice = (correctionTranscript, language, originalFields) =>
  api.post('/pricing/contest', {
    correction_transcript: correctionTranscript,
    language,
    original_fields: originalFields,
  })

// ── Consistency ────────────────────────────────────────────────
export const checkConsistency = (voiceMaterial, voiceCraft, visualTags, language) =>
  api.post('/consistency/check', {
    voice_material: voiceMaterial,
    voice_craft: voiceCraft,
    visual_tags: visualTags,
    language,
  })

// ── Catalogue ──────────────────────────────────────────────────
export const publishListing = (payload) =>
  api.post('/catalogue/publish', payload)

export const getListing = (id) =>
  api.get(`/listing/${id}`)
