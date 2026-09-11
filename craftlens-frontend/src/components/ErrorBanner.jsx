import { AlertCircle, X } from 'lucide-react'
import { useState } from 'react'

export default function ErrorBanner({ message }) {
  const [dismissed, setDismissed] = useState(false)
  if (!message || dismissed) return null
  return (
    <div className="flex items-start gap-3 bg-red-50 border border-red-200 text-red-800 rounded-xl p-4 mb-4">
      <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
      <p className="text-sm flex-1">{message}</p>
      <button onClick={() => setDismissed(true)}><X className="w-4 h-4" /></button>
    </div>
  )
}
