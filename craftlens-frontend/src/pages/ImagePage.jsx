import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Image, Upload, ArrowRight, Camera } from 'lucide-react'
import { processImage, tagImage } from '../api/client'
import { usePipeline } from '../context/PipelineContext'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

export default function ImagePage() {
  const { state, update } = usePipeline()
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const cameraInputRef = useRef(null)

  const [preview, setPreview] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [loadingMsg, setLoadingMsg] = useState('')
  const [error, setError] = useState(null)

  const handleFile = (file) => {
    if (!file) return
    setPreview(URL.createObjectURL(file))
    update({ originalImageFile: file })
    setError(null)
  }

  const handleProcess = async () => {
    if (!state.originalImageFile) return
    setError(null)
    try {
      setLoading(true)
      setLoadingMsg('Removing background…')
      const { data: imgData } = await processImage(state.originalImageFile)
      update({ imageId: imgData.image_id, processedImageUrl: imgData.processed_image_url })

      setLoadingMsg('Running CLIP visual tags…')
      const { data: tagData } = await tagImage(imgData.image_id)
      update({ visualTags: tagData.visual_tags })
      setLoading(false)
    } catch (e) {
      setLoading(false)
      setError(e.response?.data?.message || e.message)
    }
  }

  const onDrop = (e) => {
    e.preventDefault(); setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  return (
    <div className="p-4 md:p-8 bg-gray-50 min-h-screen">
      <PageHeader icon={Image} title="Image Processing" subtitle="Upload or capture a product photo. CraftLens removes the background and corrects lighting automatically." />
      <ErrorBanner message={error} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {/* Upload */}
        <Card>
          <h2 className="font-semibold text-black mb-4 text-base md:text-lg">Upload or Capture Photo</h2>
          
          {/* Upload Area */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-6 md:p-8 text-center cursor-pointer transition-colors mb-4 ${
              dragging ? 'border-black bg-gray-50' : 'border-gray-300 hover:border-gray-500 hover:bg-gray-50'
            }`}
          >
            <Upload className="w-8 h-8 md:w-10 md:h-10 text-gray-600 mx-auto mb-3" />
            <p className="text-sm text-gray-600">Tap to <span className="text-black font-medium">browse gallery</span></p>
            <p className="text-xs text-gray-400 mt-1">JPG, PNG, WebP — max 10 MB</p>
          </div>
          <input 
            ref={inputRef} 
            type="file" 
            accept="image/*" 
            className="hidden"
            onChange={(e) => handleFile(e.target.files[0])} 
          />

          {/* Camera Capture Button */}
          <button
            onClick={() => cameraInputRef.current?.click()}
            className="w-full flex items-center justify-center gap-2 bg-gray-800 hover:bg-gray-900 text-white font-semibold py-3 rounded-xl transition-colors mb-4"
          >
            <Camera className="w-5 h-5" />
            Open Camera & Capture
          </button>
          <input 
            ref={cameraInputRef} 
            type="file" 
            accept="image/*" 
            capture="environment"
            className="hidden"
            onChange={(e) => handleFile(e.target.files[0])} 
          />

          {preview && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-2">Preview</p>
              <img src={preview} alt="original" className="w-full h-48 md:h-64 object-cover rounded-xl border border-gray-200" />
            </div>
          )}

          <button
            onClick={handleProcess}
            disabled={!state.originalImageFile || loading}
            className="w-full flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold py-3 md:py-4 rounded-xl disabled:opacity-40 transition-colors text-sm md:text-base"
          >
            {loading ? <Spinner size="sm" label={loadingMsg} /> : <><Image className="w-4 h-4 md:w-5 md:h-5" /> Process Image</>}
          </button>
        </Card>

        {/* Results */}
        <div className="space-y-4">
          {state.processedImageUrl && (
            <Card>
              <p className="text-xs text-gray-500 mb-2">Processed (background removed + lighting corrected)</p>
              <img
                src={state.processedImageUrl}
                alt="processed"
                className="w-full h-48 md:h-64 object-contain rounded-xl bg-gray-50 border border-gray-200"
              />
            </Card>
          )}

          {state.visualTags && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-500 mb-3">CLIP Visual Tags</h3>
              <div className="space-y-2">
                {state.visualTags.map((tag, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-sm text-black capitalize">{tag.label}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 md:w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-gray-800 rounded-full" style={{ width: `${Math.round(tag.score * 100)}%` }} />
                      </div>
                      <span className="text-xs text-gray-500 w-8 text-right">{Math.round(tag.score * 100)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {state.imageId && (
            <button
              onClick={() => navigate('/listing')}
              className="w-full flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold py-3 md:py-4 rounded-xl transition-colors text-sm md:text-base"
            >
              Continue to Listing <ArrowRight className="w-4 h-4 md:w-5 md:h-5" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
