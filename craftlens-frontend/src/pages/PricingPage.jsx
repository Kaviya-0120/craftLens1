import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { IndianRupee, Wand2, ArrowRight, MessageSquare, RotateCcw } from 'lucide-react'
import { estimatePrice, explainPrice, contestPrice } from '../api/client'
import { usePipeline } from '../context/PipelineContext'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

export default function PricingPage() {
  const { state, update } = usePipeline()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(false)
  const [loadingMsg, setLoadingMsg] = useState('')
  const [error, setError] = useState(null)
  const [pricing, setPricing] = useState(state.pricing)
  const [explanation, setExplanation] = useState(state.pricingExplanation)
  const [contestText, setContestText] = useState('')
  const [contesting, setContesting] = useState(false)
  const [showContestBox, setShowContestBox] = useState(false)

  const listingText = state.listing
    ? `${state.listing.title_english} ${state.listing.description_english}`
    : Object.values(state.fields || {}).filter(Boolean).join(' ')

  const handleEstimate = async () => {
    if (!state.fields) return setError('Complete voice recording first.')
    setError(null); setLoading(true)
    try {
      setLoadingMsg('Searching comparable products…')
      const { data: priceData } = await estimatePrice(state.fields, listingText)
      setPricing(priceData)
      update({ pricing: priceData })

      setLoadingMsg('Generating explanation…')
      const { data: explainData } = await explainPrice(priceData, state.fields, state.language || 'en')
      setExplanation(explainData.explanation_text)
      update({ pricingExplanation: explainData.explanation_text })
    } catch (e) {
      setError(e.response?.data?.message || e.message)
    }
    setLoading(false); setLoadingMsg('')
  }

  const handleContest = async () => {
    if (!contestText.trim()) return
    setContesting(true); setError(null)
    try {
      const { data } = await contestPrice(contestText, state.language || 'en', state.fields)
      setPricing(data.updated_pricing)
      setExplanation(data.updated_explanation)
      update({
        pricing: data.updated_pricing,
        pricingExplanation: data.updated_explanation,
        fields: data.updated_fields,
      })
      setContestText(''); setShowContestBox(false)
    } catch (e) {
      setError(e.response?.data?.message || e.message)
    }
    setContesting(false)
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <PageHeader icon={IndianRupee} title="Pricing Engine" subtitle="AI-powered price estimation based on 12,600+ comparable Indian products." />
      <ErrorBanner message={error} />

      <button
        onClick={handleEstimate}
        disabled={loading || !state.fields}
        className="mb-6 flex items-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold px-6 py-3 rounded-xl disabled:opacity-40 transition-colors"
      >
        {loading ? <Spinner size="sm" label={loadingMsg} /> : <><Wand2 className="w-4 h-4" /> Estimate Price</>}
      </button>

      {pricing && (
        <div className="space-y-6">
          {/* Price range */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="text-center">
              <p className="text-xs text-gray-500 mb-1">Min Price</p>
              <p className="text-2xl font-bold text-black">₹{pricing.price_range[0].toLocaleString('en-IN')}</p>
            </Card>
            <Card className="text-center border-gray-300 bg-gray-50">
              <p className="text-xs text-gray-600 font-semibold mb-1">MEDIAN (Recommended)</p>
              <p className="text-3xl font-bold text-black">₹{pricing.median_price.toLocaleString('en-IN')}</p>
              {pricing.low_confidence && (
                <span className="inline-block mt-1 text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">Low confidence</span>
              )}
            </Card>
            <Card className="text-center">
              <p className="text-xs text-gray-500 mb-1">Max Price</p>
              <p className="text-2xl font-bold text-black">₹{pricing.price_range[1].toLocaleString('en-IN')}</p>
            </Card>
          </div>

          {/* Explanation */}
          {explanation && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Price Explanation</h3>
              <p className="text-sm text-black leading-relaxed">{explanation}</p>
            </Card>
          )}

          {/* Comparable samples */}
          {pricing.comparable_samples?.length > 0 && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-500 mb-3">
                Comparable Products ({pricing.comparable_count} found)
              </h3>
              <div className="space-y-2">
                {pricing.comparable_samples.map((s, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                    <div className="flex-1 min-w-0 mr-4">
                      <p className="text-sm text-black truncate">{s.title}</p>
                      <p className="text-xs text-gray-400 truncate">{s.category}</p>
                    </div>
                    <span className="text-sm font-semibold text-gray-700 shrink-0">
                      ₹{s.price.toLocaleString('en-IN')}
                    </span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Contest */}
          <Card>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-black">Not satisfied with the estimate?</h3>
              <button
                onClick={() => setShowContestBox(!showContestBox)}
                className="flex items-center gap-1 text-xs text-gray-600 hover:text-black"
              >
                <MessageSquare className="w-4 h-4" />
                Contest Price
              </button>
            </div>
            {showContestBox && (
              <div className="space-y-3">
                <textarea
                  rows={3}
                  placeholder="Tell us why — e.g. 'This is pure Katan silk, not regular silk. The zari is real gold thread.'"
                  value={contestText}
                  onChange={(e) => setContestText(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-amber-400"
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleContest}
                    disabled={contesting || !contestText.trim()}
                    className="flex items-center gap-2 bg-black hover:bg-gray-800 text-white text-sm font-semibold px-4 py-2 rounded-lg disabled:opacity-40 transition-colors"
                  >
                    {contesting ? <Spinner size="sm" /> : <RotateCcw className="w-4 h-4" />}
                    Re-estimate
                  </button>
                  <button onClick={() => setShowContestBox(false)} className="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </Card>

          <button
            onClick={() => navigate('/consistency')}
            className="w-full flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            Continue to Consistency Check <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  )
}
