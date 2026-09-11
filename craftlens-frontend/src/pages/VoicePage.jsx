import { useRef, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mic, Square, Send, RotateCcw, ArrowRight, Volume2 } from 'lucide-react'
import { transcribeAudio, extractFields, nextQuestion } from '../api/client'
import { usePipeline } from '../context/PipelineContext'
import PageHeader from '../components/PageHeader'
import Card from '../components/Card'
import ConfidenceBar from '../components/ConfidenceBar'
import Spinner from '../components/Spinner'
import ErrorBanner from '../components/ErrorBanner'

export default function VoicePage() {
  const { state, update } = usePipeline()
  const navigate = useNavigate()

  const [recording, setRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [waveData, setWaveData] = useState([])
  const [loadingStep, setLoadingStep] = useState(null)
  const [error, setError] = useState(null)

  // multi-turn loop state
  const [allTranscripts, setAllTranscripts] = useState([])
  const [currentFields, setCurrentFields] = useState(state.fields)
  const [currentConf, setCurrentConf] = useState(state.confidence)
  const [followup, setFollowup] = useState(state.followupQuestion)

  const mediaRef = useRef(null)
  const chunksRef = useRef([])
  const animRef = useRef(null)
  const analyserRef = useRef(null)

  // Waveform animation
  const drawWave = () => {
    if (!analyserRef.current) return
    const data = new Uint8Array(analyserRef.current.frequencyBinCount)
    analyserRef.current.getByteFrequencyData(data)
    const bars = Array.from({ length: 32 }, (_, i) =>
      Math.round((data[Math.floor(i * data.length / 32)] / 255) * 60)
    )
    setWaveData(bars)
    animRef.current = requestAnimationFrame(drawWave)
  }

  const startRecording = async () => {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      // Set up analyser for waveform
      const ctx = new AudioContext()
      const src = ctx.createMediaStreamSource(stream)
      const analyser = ctx.createAnalyser()
      analyser.fftSize = 256
      src.connect(analyser)
      analyserRef.current = analyser

      const mr = new MediaRecorder(stream)
      chunksRef.current = []
      mr.ondataavailable = (e) => chunksRef.current.push(e.data)
      mr.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach((t) => t.stop())
        cancelAnimationFrame(animRef.current)
        setWaveData([])
      }
      mr.start(100)
      mediaRef.current = mr
      setRecording(true)
      drawWave()
    } catch (e) {
      setError('Microphone access denied. Please allow microphone in browser settings.')
    }
  }

  const stopRecording = () => {
    mediaRef.current?.stop()
    setRecording(false)
  }

  const handleTranscribeAndExtract = async (blob, isFollowup = false) => {
    setError(null)
    const file = new File([blob], 'recording.webm', { type: 'audio/webm' })

    try {
      setLoadingStep('Transcribing audio…')
      const { data: tData } = await transcribeAudio(file)

      const prev = isFollowup ? allTranscripts.join(' ') : null
      const newTranscripts = [...allTranscripts, tData.transcript]
      setAllTranscripts(newTranscripts)

      update({ transcript: tData.transcript, language: tData.detected_language })

      setLoadingStep('Extracting craft fields…')
      const { data: fData } = await extractFields(tData.transcript, tData.detected_language, prev)

      setCurrentFields(fData.fields)
      setCurrentConf(fData.confidence)
      update({ fields: fData.fields, confidence: fData.confidence })

      setLoadingStep('Checking follow-up…')
      const { data: qData } = await nextQuestion(fData.fields, fData.confidence, tData.detected_language)

      setFollowup(qData)
      update({ followupQuestion: qData })
      setLoadingStep(null)
    } catch (e) {
      setLoadingStep(null)
      setError(e.response?.data?.message || e.message)
    }
  }

  const handleSubmit = () => {
    if (audioBlob) handleTranscribeAndExtract(audioBlob, allTranscripts.length > 0)
  }

  const handleReset = () => {
    setAudioBlob(null); setAudioUrl(null); setAllTranscripts([])
    setCurrentFields(null); setCurrentConf(null); setFollowup(null)
    update({ transcript: null, language: null, fields: null, confidence: null, followupQuestion: null })
  }

  const CONF_FIELDS = ['material', 'craft_technique', 'size', 'region']

  return (
    <div className="p-4 md:p-8 bg-gray-50 min-h-screen">
      <PageHeader icon={Mic} title="Voice Recording" subtitle="Speak about your craft product. CraftLens extracts all product details automatically." />
      <ErrorBanner message={error} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {/* Recorder */}
        <Card>
          <h2 className="font-semibold text-black mb-4">
            {followup?.needs_followup ? '🎙 Answer Follow-up Question' : '🎙 Record Your Product'}
          </h2>

          {followup?.needs_followup && (
            <div className="mb-4 p-4 bg-gray-50 border border-gray-300 rounded-xl flex gap-3">
              <Volume2 className="w-5 h-5 text-black shrink-0 mt-0.5" />
              <div>
                <p className="text-xs text-gray-600 font-semibold mb-1">Follow-up — {followup.field?.replace(/_/g,' ')}</p>
                <p className="text-sm text-black font-medium">{followup.question_text}</p>
              </div>
            </div>
          )}

          {/* Waveform */}
          <div className="h-16 flex items-center justify-center gap-0.5 bg-black rounded-xl mb-5 overflow-hidden">
            {recording
              ? waveData.map((h, i) => (
                  <div key={i} className="w-1.5 bg-gray-400 rounded-full transition-all duration-75" style={{ height: `${Math.max(4, h)}px` }} />
                ))
              : Array.from({ length: 32 }).map((_, i) => (
                  <div key={i} className="w-1.5 bg-gray-700 rounded-full" style={{ height: '4px' }} />
                ))
            }
          </div>

          <div className="flex gap-3 justify-center mb-4">
            {!recording ? (
              <button
                onClick={startRecording}
                disabled={!!loadingStep}
                className="flex items-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold px-6 py-3 rounded-xl transition-colors disabled:opacity-50"
              >
                <Mic className="w-5 h-5" /> Record
              </button>
            ) : (
              <button
                onClick={stopRecording}
                className="flex items-center gap-2 bg-gray-700 hover:bg-gray-800 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
              >
                <Square className="w-4 h-4" /> Stop
              </button>
            )}
            {audioBlob && !recording && (
              <button
                onClick={handleSubmit}
                disabled={!!loadingStep}
                className="flex items-center gap-2 bg-gray-800 hover:bg-black text-white font-semibold px-6 py-3 rounded-xl transition-colors disabled:opacity-50"
              >
                {loadingStep ? <Spinner size="sm" /> : <Send className="w-4 h-4" />}
                {loadingStep || 'Analyse'}
              </button>
            )}
            {allTranscripts.length > 0 && (
              <button onClick={handleReset} className="p-3 rounded-xl border border-gray-200 hover:bg-gray-50 text-gray-500">
                <RotateCcw className="w-4 h-4" />
              </button>
            )}
          </div>

          {audioUrl && !recording && (
            <audio controls src={audioUrl} className="w-full rounded-lg" />
          )}
        </Card>

        {/* Results */}
        <div className="space-y-4">
          {/* Transcript */}
          {state.transcript && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-500 mb-2">Transcript · {state.language?.toUpperCase()}</h3>
              <p className="text-black text-sm leading-relaxed">{state.transcript}</p>
            </Card>
          )}

          {/* Fields */}
          {currentFields && (
            <Card>
              <h3 className="text-sm font-semibold text-gray-500 mb-3">Extracted Fields</h3>
              <div className="grid grid-cols-2 gap-3 mb-4">
                {Object.entries(currentFields).filter(([, v]) => v).map(([k, v]) => (
                  <div key={k} className="bg-gray-50 rounded-lg p-2 border border-gray-200">
                    <span className="text-xs text-gray-600 capitalize">{k.replace(/_/g,' ')}</span>
                    <p className="text-sm font-semibold text-black truncate">{String(v)}</p>
                  </div>
                ))}
              </div>
              {currentConf && (
                <>
                  <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Confidence</h3>
                  <div className="space-y-2">
                    {CONF_FIELDS.map((f) => (
                      <ConfidenceBar key={f} label={f} value={currentConf[f]} />
                    ))}
                  </div>
                </>
              )}
            </Card>
          )}

          {/* Navigate next */}
          {currentFields && !followup?.needs_followup && (
            <button
              onClick={() => navigate('/image')}
              className="w-full flex items-center justify-center gap-2 bg-black hover:bg-gray-800 text-white font-semibold py-3 rounded-xl transition-colors"
            >
              Continue to Image <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
