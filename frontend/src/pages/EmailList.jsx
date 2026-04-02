import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { RefreshCw, Zap, Filter } from 'lucide-react'
import { listEmails, fetchEmails, classifyAll } from '../api'
import StatusBadge from '../components/StatusBadge'
import CategoryBadge from '../components/CategoryBadge'

export default function EmailList() {
  const [emails, setEmails] = useState([])
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const load = async () => {
    try {
      const { data } = await listEmails(filter || undefined)
      setEmails(data)
    } catch {
      /* empty */
    }
  }

  useEffect(() => { load() }, [filter])

  const handleFetch = async () => {
    setLoading(true)
    try {
      await fetchEmails()
      await load()
    } catch {
      /* empty */
    }
    setLoading(false)
  }

  const handleClassifyAll = async () => {
    setLoading(true)
    try {
      await classifyAll()
      await load()
    } catch {
      /* empty */
    }
    setLoading(false)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Email</h1>
        <div className="flex gap-3">
          <div className="flex items-center gap-2 bg-white border rounded-lg px-3 py-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-transparent border-none outline-none text-sm"
            >
              <option value="">Tutte</option>
              <option value="new">Nuove</option>
              <option value="classified">Classificate</option>
              <option value="replied">Con risposta</option>
            </select>
          </div>
          <button onClick={handleFetch} disabled={loading} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Recupera
          </button>
          <button onClick={handleClassifyAll} disabled={loading} className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50">
            <Zap className="h-4 w-4" />
            Classifica
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Mittente</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Oggetto</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Data</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Stato</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Categoria</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Confidenza</th>
            </tr>
          </thead>
          <tbody>
            {emails.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-12 text-gray-400">
                  Nessuna email. Premi "Recupera" per caricare la casella.
                </td>
              </tr>
            ) : (
              emails.map((em) => (
                <tr
                  key={em.id}
                  onClick={() => navigate(`/emails/${em.id}`)}
                  className="border-b hover:bg-gray-50 cursor-pointer transition-colors"
                >
                  <td className="px-4 py-3 text-sm">{em.sender?.split('<')[0]?.trim()}</td>
                  <td className="px-4 py-3 text-sm font-medium text-gray-800 max-w-xs truncate">{em.subject}</td>
                  <td className="px-4 py-3 text-sm text-gray-500">{new Date(em.date).toLocaleDateString('it-IT')}</td>
                  <td className="px-4 py-3"><StatusBadge status={em.status} /></td>
                  <td className="px-4 py-3"><CategoryBadge category={em.category} /></td>
                  <td className="px-4 py-3 text-sm">
                    {em.confidence != null && (
                      <span className={`font-medium ${em.confidence > 0.7 ? 'text-green-600' : em.confidence > 0.4 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {Math.round(em.confidence * 100)}%
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
