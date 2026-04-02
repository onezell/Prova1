const colors = {
  richiesta_info: 'bg-purple-100 text-purple-800',
  reclamo: 'bg-red-100 text-red-800',
  supporto_tecnico: 'bg-orange-100 text-orange-800',
  preventivo: 'bg-indigo-100 text-indigo-800',
  collaborazione: 'bg-teal-100 text-teal-800',
  spam: 'bg-gray-100 text-gray-500',
  altro: 'bg-gray-100 text-gray-700',
}

const labels = {
  richiesta_info: 'Richiesta Info',
  reclamo: 'Reclamo',
  supporto_tecnico: 'Supporto Tecnico',
  preventivo: 'Preventivo',
  collaborazione: 'Collaborazione',
  spam: 'Spam',
  altro: 'Altro',
}

export default function CategoryBadge({ category }) {
  if (!category) return null
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[category] || colors.altro}`}>
      {labels[category] || category}
    </span>
  )
}
