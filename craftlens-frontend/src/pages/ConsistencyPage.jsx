import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ShieldCheck, AlertTriangle, CheckCircle2, ArrowRight, Wand2 } from 'lucide-react'
import { checkConsistency } from '../api/client'
import { usePipeline } from '../context/PipelineContext'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

export default function ConsistencyPage() {
  const { state, update } = usePipeline()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(state.consistencyResult)

  const canCheck = state.fields && state.visualTags

  const handleCheck = async () => {
    if (!canCheck) return setError('Complete Voice and Image steps first.')
    setError(null); setLoading(true)
    try {
      const { data } = await checkConsistency(
        state.fields.material || '',
        state.fields.craft_technique || '',
        state.visualTags,
        state.language || 'en'
      )
      setResult(data)
      update({ consistencyResult: data })
    } catch (e) {
      setError(e.response?.data?.message || e.message)
    }
    setLoading(false)
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <PageHeader
        icon={ShieldCheck}
        title="Consistency Check"
        subtitle="Compares what the artisan said with what the product photo shows using CLIP visual AI."
      />
      <ErrorBanner message={error} />

      {!canCheck && (
        <div className="bg-gray-50 border border-gray-300 rounded-xl p-4 mb-6 text-sm text-gray-700">
          Complete the Voice and Image steps first to enable consistency checking.
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inputs summary */}
        <Card>
          <h2 className="font-semibold text-black mb-4">What we're comparing</h2>
          <div className="space-y-4">
            <div className="p-3 bg-blue-50 rounded-xl">
              <p className="text-xs text-blue-600 font-semibold mb-1">🎙 Voice Claims</p>
              <p className="text-sm text-blue-900">
                <strong>Material:</strong> {state.fields?.material || '—'}<br />
                <strong>Craft:</strong> {state.fields?.craft_technique || '—'}
              </p>
            </div>
            <div className="p-3 bg-purple-50 rounded-xl">
              <p className="text-xs text-purple-600 font-semibold mb-1">📷 Visual Tags (CLIP)</p>
              {state.visualTags ? (
                <div className="space-y-1">
                  {state.visualTags.map((t, i) => (
                    <p key={i} className="text-sm text-purple-900">
                      {t.label} — <span className="font-semibold">{Math.round(t.score * 100)}%</span>
                    </p>
                  ))}
                </div>
              ) : <p className="text-sm text-purple-400">No image processed yet</p>}
            </div>
          </div>

          <button
            onClick={handleCheck}
            disabled={loading || !canCheck}
            className="mt-4 w-full flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold py-3 rounded-xl disabled:opacity-40 transition-colors"
          >
            {loading ? <Spinner size="sm" label="Checking…" /> : <><Wand2 className="w-4 h-4" /> Run Consistency Check</>}
          </button>
        </Card>

        {/* Result */}
        <div>
          {result && (
            <Card>
              {result.mismatch ? (
                <>
                  <div className="flex items-center gap-3 mb-4 p-3 bg-red-50 rounded-xl">
                    <AlertTriangle className="w-6 h-6 text-red-500 shrink-0" />
                    <div>
                      <p className="font-semibold text-red-700">Mismatch Detected</p>
                      <p className="text-xs text-red-500">
                        Similarity score: {(result.similarity_score * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <p className="text-xs text-blue-500 mb-1">Voice claim</p>
                      <p className="text-sm font-semibold text-blue-900">{result.voice_claim}</p>
                    </div>
                    <div className="p-3 bg-purple-50 rounded-lg">
                      <p className="text-xs text-purple-500 mb-1">Top visual tag</p>
                      <p className="text-sm font-semibold text-purple-900">{result.closest_visual_tag}</p>
                    </div>
                  </div>
                  {result.confirmation_question && (
                    <div className="p-4 bg-gray-50 border border-gray-300 rounded-xl">
                      <p className="text-xs text-gray-600 font-semibold mb-1">Confirmation Question for Artisan</p>
                      <p className="text-sm text-black font-medium">{result.confirmation_question}</p>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex items-center gap-3 p-4 bg-green-50 rounded-xl">
                  <CheckCircle2 className="w-8 h-8 text-green-500" />
                  <div>
                    <p className="font-semibold text-green-700">All Good — No Mismatch</p>
                    <p className="text-sm text-green-600">
                      Voice claims match visual tags.
                      Similarity: {(result.similarity_score * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              )}

              <button
                onClick={() => navigate('/catalogue')}
                className="mt-4 w-full flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold py-3 rounded-xl transition-colors"
              >
                Continue to Publish <ArrowRight className="w-4 h-4" />
              </button>
            </Card>
          )}

          {!result && (
            <Card className="flex items-center justify-center h-48 text-gray-400 text-sm">
              Run the check to see results
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
