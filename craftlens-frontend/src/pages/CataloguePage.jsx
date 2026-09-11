import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BookOpen, Send, ExternalLink, CheckCircle2, Copy, Store } from 'lucide-react'
import { publishListing } from '../api/client'
import { usePipeline } from '../context/PipelineContext'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

export default function CataloguePage() {
  const navigate = useNavigate()
  const { state, update } = usePipeline()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [listingId, setListingId] = useState(state.publishedListingId)
  const [copied, setCopied] = useState(false)

  const price = state.pricing?.median_price || state.fields?.price_hint || 0
  const shareUrl = listingId ? `http://localhost:8000/listing/${listingId}` : null

  const canPublish = state.listing && state.fields

  const handlePublish = async () => {
    if (!canPublish) return setError('Complete listing generation before publishing.')
    setError(null); setLoading(true)
    try {
      // Get artisan profile from localStorage
      const artisanProfile = JSON.parse(localStorage.getItem('artisanProfile') || '{}')
      
      const publishedProduct = {
        id: `listing_${Date.now()}`,
        image_url: state.processedImageUrl || '/artisan-craft.jpg',
        title_english: state.listing.title_english,
        title_regional: state.listing.title_regional,
        description_english: state.listing.description_english,
        description_regional: state.listing.description_regional,
        price: price,
        price_min: state.pricing?.price_range?.[0] || Math.round(price * 0.8),
        price_max: state.pricing?.price_range?.[1] || Math.round(price * 1.2),
        artisan_name: artisanProfile.name || 'Artisan',
        artisan_region: state.fields?.region || artisanProfile.region || 'India',
        artisan_phone: artisanProfile.phone || '+919876543210',
        artisan_whatsapp: artisanProfile.whatsapp || artisanProfile.phone || '+919876543210',
        artisan_email: artisanProfile.email || 'artisan@email.com',
        craft_type: state.fields?.craft_technique || artisanProfile.craftType || 'Handcraft',
        material: state.fields?.material || 'Natural',
        material_origin: `Naturally sourced ${state.fields?.material || 'materials'} from ${state.fields?.region || artisanProfile.region || 'local artisan communities'}. Each piece is crafted with authentic traditional methods passed down through generations.`,
        experience_years: parseInt(artisanProfile.experience) || 10,
        size: state.fields?.size || 'Standard',
        color: state.fields?.color || 'Natural',
      }

      // Save to localStorage
      const existingListings = JSON.parse(localStorage.getItem('publishedListings') || '[]')
      existingListings.unshift(publishedProduct) // Add to beginning
      localStorage.setItem('publishedListings', JSON.stringify(existingListings))

      // Also call backend API
      const { data } = await publishListing({
        image_url: state.processedImageUrl || '/static/placeholder.png',
        title_regional: state.listing.title_regional,
        title_english: state.listing.title_english,
        description_regional: state.listing.description_regional,
        description_english: state.listing.description_english,
        price: price,
        fields: state.fields,
      })
      setListingId(data.listing_id)
      update({ publishedListingId: data.listing_id })
    } catch (e) {
      setError(e.response?.data?.message || e.message)
    }
    setLoading(false)
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(shareUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <PageHeader icon={BookOpen} title="Publish to Catalogue" subtitle="Review and publish the final listing. Get a shareable URL." />
      <ErrorBanner message={error} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Preview */}
        <div className="space-y-4">
          <Card>
            <h2 className="font-semibold text-black mb-4">Listing Preview</h2>

            {state.processedImageUrl && (
              <img
                src={state.processedImageUrl}
                alt="product"
                className="w-full h-48 object-contain rounded-xl bg-gray-50 mb-4"
              />
            )}

            {state.listing ? (
              <>
                <h3 className="font-bold text-lg text-black">{state.listing.title_english}</h3>
                <p className="text-sm text-gray-500 mt-1 mb-3">{state.listing.title_regional}</p>
                <p className="text-sm text-gray-700 leading-relaxed line-clamp-4">{state.listing.description_english}</p>

                {price > 0 && (
                  <div className="mt-4 flex items-center gap-2">
                    <span className="text-2xl font-bold text-black">₹{Number(price).toLocaleString('en-IN')}</span>
                    <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                      {state.pricing?.low_confidence ? 'Estimated' : 'Market-based'}
                    </span>
                  </div>
                )}
              </>
            ) : (
              <p className="text-sm text-gray-600">Complete the Listing step first.</p>
            )}
          </Card>

          {/* Fields summary */}
          {state.fields && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-500 mb-3">Product Details</h3>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(state.fields).filter(([, v]) => v).map(([k, v]) => (
                  <div key={k} className="bg-gray-50 rounded-lg p-2">
                    <p className="text-xs text-gray-600 capitalize">{k.replace(/_/g, ' ')}</p>
                    <p className="text-sm font-medium text-black truncate">{String(v)}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Publish panel */}
        <div className="space-y-4">
          {!listingId ? (
            <Card>
              <h2 className="font-semibold text-black mb-2">Ready to Publish?</h2>
              <p className="text-sm text-gray-500 mb-6">
                This will save the listing to the CraftLens catalogue and generate a shareable URL.
              </p>
              <button
                onClick={handlePublish}
                disabled={loading || !canPublish}
                className="w-full flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold py-3 rounded-xl disabled:opacity-40 transition-colors text-lg"
              >
                {loading ? <Spinner size="sm" label="Publishing…" /> : <><Send className="w-5 h-5" /> Publish Listing</>}
              </button>
            </Card>
          ) : (
            <Card className="border-green-200 bg-green-50">
              <div className="flex items-center gap-3 mb-4">
                <CheckCircle2 className="w-8 h-8 text-green-500" />
                <div>
                  <p className="font-bold text-green-800">Published Successfully!</p>
                  <p className="text-xs text-green-600">Listing ID: {listingId}</p>
                </div>
              </div>

              <div className="bg-white rounded-xl p-3 border border-green-200 mb-3">
                <p className="text-xs text-gray-500 mb-1">Shareable URL</p>
                <p className="text-sm text-gray-700 font-mono break-all">{shareUrl}</p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleCopy}
                  className="flex-1 flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
                >
                  {copied ? <CheckCircle2 className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? 'Copied!' : 'Copy URL'}
                </button>
                <button
                  onClick={() => navigate('/marketplace')}
                  className="flex-1 flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
                >
                  <Store className="w-4 h-4" /> View Marketplace
                </button>
              </div>
            </Card>
          )}

          {/* QR stub */}
          {listingId && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-500 mb-3">QR Code (stub)</h3>
              <div className="w-32 h-32 mx-auto bg-gray-100 rounded-xl flex items-center justify-center">
                <p className="text-xs text-gray-400 text-center px-2">QR generation<br/>coming soon</p>
              </div>
              <p className="text-xs text-center text-gray-400 mt-2">
                Print this QR at the artisan stall to share the listing instantly
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
