export default function ConfidenceBar({ label, value }) {
  const pct = Math.round((value ?? 0) * 100)
  const color =
    pct >= 70 ? 'bg-green-500' : pct >= 40 ? 'bg-amber-400' : 'bg-red-400'

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-gray-600">
        <span className="capitalize">{label.replace(/_/g, ' ')}</span>
        <span className="font-semibold">{pct}%</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
