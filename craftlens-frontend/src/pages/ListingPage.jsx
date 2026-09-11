import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Tag, Wand2, ArrowRight, Edit3, Check } from 'lucide-react'
import { generateListing } from '../api/client'
import { usePipeline } from '../context/PipelineContext'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

function EditableField({ label, value, onChange }) {
  const [editing, setEditing] = useState(false)
  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-1">
        <label className="text-xs text-gray-500 font-semibold uppercase tracking-wide">{label}</label>
        <button onClick={() => setEditing(!editing)} className="text-gray-600 hover:text-black">
          {editing ? <Check className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
        </button>
      </div>
      {editing ? (
        <textarea
          className="w-full border border-gray-300 rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-black"
          rows={3}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      ) : (
        <p className="text-sm text-black bg-gray-50 rounded-lg p-3 leading-relaxed border border-gray-200">{value}</p>
      )}
    </div>
  )
}

export default function ListingPage() {
  const { state, update } = usePipeline()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [listing, setListing] = useState(state.listing)

  const handleGenerate = async () => {
    if (!state.fields) return setError('Complete voice recording first.')
    setError(null); setLoading(true)
    try {
      const { data } = await generateListing(
        state.fields,
        state.transcript || '',
        state.language || 'en'
      )
      setListing(data)
      update({ listing: data })
    } catch (e) {
      setError(e.response?.data?.message || e.message)
    }
    setLoading(false)
  }

  const update_field = (key) => (val) => {
    const updated = { ...listing, [key]: val }
    setListing(updated)
    update({ listing: updated })
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <PageHeader icon={Tag} title="Listing Generation" subtitle="AI-generated SEO-friendly titles and descriptions in English and regional language." />
      <ErrorBanner message={error} />

      {!state.fields && (
        <div className="bg-gray-100 border border-gray-300 rounded-xl p-4 mb-6 text-sm text-gray-700">
          Complete the Voice step first to extract product fields.
        </div>
      )}

      <button
        onClick={handleGenerate}
        disabled={loading || !state.fields}
        className="mb-6 flex items-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold px-6 py-3 rounded-xl disabled:opacity-40 transition-colors"
      >
        {loading ? <Spinner size="sm" label="Generating…" /> : <><Wand2 className="w-4 h-4" /> Generate Listing</>}
      </button>

      {listing && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <h2 className="font-semibold text-black mb-4">🇬🇧 English</h2>
            <EditableField label="Title" value={listing.title_english} onChange={update_field('title_english')} />
            <EditableField label="Description" value={listing.description_english} onChange={update_field('description_english')} />
          </Card>
          <Card>
            <h2 className="font-semibold text-black mb-4">🇮🇳 Regional Language</h2>
            <EditableField label="Title" value={listing.title_regional} onChange={update_field('title_regional')} />
            <EditableField label="Description" value={listing.description_regional} onChange={update_field('description_regional')} />
          </Card>

          <div className="lg:col-span-2">
            <button
              onClick={() => navigate('/pricing')}
              className="w-full flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold py-3 rounded-xl transition-colors"
            >
              Continue to Pricing <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
