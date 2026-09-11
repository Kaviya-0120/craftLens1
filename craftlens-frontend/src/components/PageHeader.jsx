export default function PageHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex items-start gap-4 mb-8">
      {Icon && (
        <div className="p-3 bg-gray-100 rounded-xl">
          <Icon className="w-6 h-6 text-black" />
        </div>
      )}
      <div>
        <h1 className="text-2xl font-bold text-black">{title}</h1>
        {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
      </div>
    </div>
  )
}
