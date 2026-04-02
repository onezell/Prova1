const colors = {
  new: 'bg-yellow-100 text-yellow-800',
  classified: 'bg-blue-100 text-blue-800',
  pending_approval: 'bg-orange-100 text-orange-800',
  approved: 'bg-emerald-100 text-emerald-800',
  replied: 'bg-green-100 text-green-800',
  skipped: 'bg-gray-100 text-gray-800',
}

const labels = {
  new: 'Nuova',
  classified: 'Classificata',
  pending_approval: 'In approvazione',
  approved: 'Approvata',
  replied: 'Risposta inviata',
  skipped: 'Saltata',
}

export default function StatusBadge({ status }) {
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || colors.new}`}>
      {labels[status] || status}
    </span>
  )
}
