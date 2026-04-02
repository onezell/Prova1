import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Zap, Send, RefreshCw } from 'lucide-react'
import { getEmail, classifyEmail, sendReply, generateReply } from '../api'
import StatusBadge from '../components/StatusBadge'
import CategoryBadge from '../components/CategoryBadge'

export default function EmailDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [email, setEmail] = useState(null)
  const [replyText, setReplyText] = useState('')
  const [instructions, setInstructions] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    getEmail(id).then(({ data }) => {
      setEmail(data)
      if (data.suggested_reply) setReplyText(data.suggested_reply)
    })
  }, [id])

  const handleClassify = async () => {
    setLoading(true)
    try {
      const { data } = await classifyEmail(id)
      setEmail((prev) => ({
        ...prev,
        category: data.classification.category,
        confidence: data.classification.confidence,
        suggested_reply: data.classification.suggested_reply,
        status: 'classified',
      }))
      setReplyText(data.classification.suggested_reply)
      setMessage('Email classificata')
    } catch (e) {
      setMessage(`Errore: ${e.response?.data?.detail || e.message}`)
    }
    setLoading(false)
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const { data } = await generateReply(id, instructions)
      setReplyText(data.reply)
      setMessage('Risposta generata')
    } catch (e) {
      setMessage(`Errore: ${e.response?.data?.detail || e.message}`)
    }
    setLoading(false)
  }

  const handleSend = async () => {
    if (!replyText.trim()) return
    setLoading(true)
    try {
      await sendReply(id, replyText)
      setEmail((prev) => ({ ...prev, status: 'replied', reply_sent: true }))
      setMessage('Risposta inviata!')
    } catch (e) {
      setMessage(`Errore invio: ${e.response?.data?.detail || e.message}`)
    }
    setLoading(false)
  }

  if (!email) return <div className="text-center py-12 text-gray-400">Caricamento...</div>

  return (
    <div>
      <button onClick={() => navigate('/emails')} className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6">
        <ArrowLeft className="h-4 w-4" /> Torna alla lista
      </button>

      {message && (
        <div className="mb-4 p-3 bg-blue-50 text-blue-700 rounded-lg">{message}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Email content */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <div className="flex items-center gap-2 mb-4">
            <StatusBadge status={email.status} />
            <CategoryBadge category={email.category} />
            {email.confidence != null && (
              <span className="text-sm text-gray-500">
                Confidenza: {Math.round(email.confidence * 100)}%
              </span>
            )}
          </div>

          <h2 className="text-xl font-bold text-gray-800 mb-2">{email.subject}</h2>
          <p className="text-sm text-gray-500 mb-1"><strong>Da:</strong> {email.sender}</p>
          <p className="text-sm text-gray-500 mb-4"><strong>Data:</strong> {new Date(email.date).toLocaleString('it-IT')}</p>

          <div className="border-t pt-4">
            <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans leading-relaxed max-h-96 overflow-y-auto">
              {email.body || '(nessun contenuto testuale)'}
            </pre>
          </div>

          {email.status === 'new' && (
            <button
              onClick={handleClassify}
              disabled={loading}
              className="mt-4 flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              <Zap className="h-4 w-4" /> Classifica
            </button>
          )}
        </div>

        {/* Reply section */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">Risposta</h3>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-600 mb-1">Istruzioni per la generazione</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                placeholder="es. Rispondi in modo formale, proponi un appuntamento..."
                className="flex-1 border rounded-lg px-3 py-2 text-sm"
              />
              <button
                onClick={handleGenerate}
                disabled={loading}
                className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Genera
              </button>
            </div>
          </div>

          <textarea
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            rows={12}
            className="w-full border rounded-lg px-3 py-2 text-sm resize-y"
            placeholder="Scrivi o genera una risposta..."
          />

          <button
            onClick={handleSend}
            disabled={loading || !replyText.trim() || email.reply_sent}
            className="mt-4 flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
            {email.reply_sent ? 'Risposta Inviata' : 'Invia Risposta'}
          </button>
        </div>
      </div>
    </div>
  )
}
