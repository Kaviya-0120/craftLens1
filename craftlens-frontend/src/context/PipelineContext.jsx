import { createContext, useContext, useState } from 'react'

const PipelineContext = createContext(null)

export function PipelineProvider({ children }) {
  const [state, setState] = useState({
    // Phase 1
    transcript: null,
    language: null,
    fields: null,
    confidence: null,
    // Phase 2
    followupQuestion: null,
    // Phase 3
    imageId: null,
    processedImageUrl: null,
    originalImageFile: null,
    // Phase 4
    listing: null,
    // Phase 5
    pricing: null,
    pricingExplanation: null,
    // Phase 6
    visualTags: null,
    consistencyResult: null,
    // Phase 8
    publishedListingId: null,
  })

  const update = (patch) => setState((s) => ({ ...s, ...patch }))
  const reset = () => setState({})

  return (
    <PipelineContext.Provider value={{ state, update, reset }}>
      {children}
    </PipelineContext.Provider>
  )
}

export const usePipeline = () => useContext(PipelineContext)
