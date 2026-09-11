export default function Spinner({ size = 'md', label }) {
  const sz = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-10 h-10' : 'w-6 h-6'
  return (
    <div className="flex items-center gap-2">
      <div className={`${sz} border-2 border-amber-300 border-t-amber-700 rounded-full animate-spin`} />
      {label && <span className="text-sm text-amber-700">{label}</span>}
    </div>
  )
}
