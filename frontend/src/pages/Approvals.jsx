import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Eye, Send } from 'lucide-react'
import { listEmails, approveEmail, rejectEmail, sendReply } from '../api'
import StatusBadge from '../components/StatusBadge'
import CategoryBadge from '../components/CategoryBadge'

export default function Approvals() {
  const [emails, setEmails] = useState([])
  const [selected, setSelected] = useState(null)
  const [replyText, setReplyText] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [tab, setTab] = useState('pending') // pending | approved

  const load = async () => {
    const status = tab === 'pending' ? 'pending_approval' : 'approved'
    const { data } = await listEmails({ status, page_size: 50 })
    setEmails(data.emails)
  }

  useEffect(() => { load(); setSelected(null) }, [tab])

  const handleSelect = (em) => {
    setSelected(em)
    setReplyText(em.suggested_reply || '')
    setMessage('')
  }

  const handleApprove = async () => {
    if (!selected) return
    setLoading(true)
    try {
      await approveEmail(selected.id, replyText !== selected.suggested_reply ? replyText : null)
      setMessage('Approvata!')
      await load()
      setSelected(null)
    } catch (e) {
      setMessage(`Errore: ${e.response?.data?.detail || e.message}`)
    }
    setLoading(false)
  }

  const handleReject = async () => {
    if (!selected) return
    setLoading(true)
    try {
      await rejectEmail(selected.id)
      setMessage('Rifiutata, torna in classificata')
      await load()
      setSelected(null)
    } catch (e) {
      setMessage(`Errore: ${e.response?.data?.detail || e.message}`)
    }
    setLoading(false)
  }

  const handleSend = async () => {
    if (!selected) return
    setLoading(true)
    try {
      await sendReply(selected.id, replyText)
      setMessage('Risposta inviata!')
      await load()
      setSelected(null)
    } catch (e) {
      setMessage(`Errore invio: ${e.response?.data?.detail || e.message}`)
    }
    setLoading(false)
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Coda Approvazioni</h1>

      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setTab('pending')}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'pending' ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-600'}`}
        >
          In attesa
        </button>
        <button
          onClick={() => setTab('approved')}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${tab === 'approved' ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-600'}`}
        >
          Approvate (da inviare)
        </button>
      </div>

      {message && (
        <div className="mb-4 p-3 bg-blue-50 text-blue-700 rounded-lg">{message}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* List */}
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          {emails.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              {tab === 'pending' ? 'Nessuna email in attesa di approvazione' : 'Nessuna email approvata da inviare'}
            </div>
          ) : (
            <div className="divide-y">
              {emails.map((em) => (
                <div
                  key={em.id}
                  onClick={() => handleSelect(em)}
                  className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${selected?.id === em.id ? 'bg-blue-50' : ''}`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-800 truncate">{em.sender?.split('<')[0]?.trim()}</span>
                    <CategoryBadge category={em.category} />
                  </div>
                  <p className="text-sm text-gray-600 truncate">{em.subject}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <StatusBadge status={em.status} />
                    {em.confidence != null && (
                      <span className="text-xs text-gray-400">{Math.round(em.confidence * 100)}%</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Detail + Actions */}
        {selected && (
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-2">{selected.subject}</h3>
            <p className="text-sm text-gray-500 mb-3">Da: {selected.sender}</p>

            <div className="bg-gray-50 rounded-lg p-3 mb-4 max-h-40 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">{selected.body}</pre>
            </div>

            <label className="block text-sm font-medium text-gray-600 mb-1">Risposta proposta</label>
            <textarea
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              rows={8}
              className="w-full border rounded-lg px-3 py-2 text-sm resize-y mb-4"
            />

            <div className="flex gap-2">
              {tab === 'pending' && (
                <>
                  <button onClick={handleApprove} disabled={loading} className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50">
                    <CheckCircle className="h-4 w-4" /> Approva
                  </button>
                  <button onClick={handleReject} disabled={loading} className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50">
                    <XCircle className="h-4 w-4" /> Rifiuta
                  </button>
                </>
              )}
              {tab === 'approved' && (
                <button onClick={handleSend} disabled={loading} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50">
                  <Send className="h-4 w-4" /> Invia
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
