import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { RefreshCw, Zap, Mail, CheckCircle, AlertTriangle, BarChart3, Database, ClipboardCheck } from 'lucide-react'
import { getStats, fetchEmails, classifyAll, seedData } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const loadStats = async () => {
    try {
      const { data } = await getStats()
      setStats(data)
    } catch {
      /* empty */
    }
  }

  useEffect(() => { loadStats() }, [])

  const handleAction = async (action, label) => {
    setLoading(true)
    setMessage('')
    try {
      const { data } = await action()
      setMessage(`${label}: ${JSON.stringify(data).slice(0, 100)}`)
      await loadStats()
    } catch (e) {
      setMessage(`Errore: ${e.response?.data?.detail || e.message}`)
    }
    setLoading(false)
  }

  const statCards = stats ? [
    { label: 'Totale Email', value: stats.total, icon: Mail, color: 'bg-blue-500' },
    { label: 'Nuove', value: stats.by_status?.new || 0, icon: AlertTriangle, color: 'bg-yellow-500' },
    { label: 'Classificate', value: stats.by_status?.classified || 0, icon: BarChart3, color: 'bg-purple-500' },
    { label: 'In Approvazione', value: stats.pending_approval || 0, icon: ClipboardCheck, color: 'bg-orange-500' },
    { label: 'Approvate', value: stats.by_status?.approved || 0, icon: CheckCircle, color: 'bg-emerald-500' },
    { label: 'Risposte Inviate', value: stats.by_status?.replied || 0, icon: CheckCircle, color: 'bg-green-500' },
  ] : []

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <div className="flex gap-3">
          <button
            onClick={() => handleAction(seedData, 'Seed')}
            disabled={loading}
            className="flex items-center gap-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
          >
            <Database className="h-4 w-4" />
            Carica Demo
          </button>
          <button
            onClick={() => handleAction(fetchEmails, 'Fetch')}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Recupera Email
          </button>
          <button
            onClick={() => handleAction(classifyAll, 'Classificazione')}
            disabled={loading}
            className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            <Zap className="h-4 w-4" />
            Classifica Tutte
          </button>
        </div>
      </div>

      {message && (
        <div className="mb-6 p-3 bg-blue-50 text-blue-700 rounded-lg text-sm">{message}</div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-500">{label}</p>
                <p className="text-2xl font-bold mt-1">{value}</p>
              </div>
              <div className={`${color} p-2 rounded-lg`}>
                <Icon className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {stats && Object.keys(stats.by_category).length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Distribuzione per Categoria</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(stats.by_category).map(([cat, count]) => (
              <div key={cat} className="bg-gray-50 rounded-lg p-3 text-center">
                <p className="text-2xl font-bold">{count}</p>
                <p className="text-sm text-gray-500 capitalize">{cat.replace('_', ' ')}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-4 mt-6">
        <Link to="/emails" className="text-blue-600 hover:underline">Lista email</Link>
        <Link to="/approvals" className="text-orange-600 hover:underline">Coda approvazioni</Link>
        <Link to="/templates" className="text-purple-600 hover:underline">Template risposte</Link>
      </div>
    </div>
  )
}
