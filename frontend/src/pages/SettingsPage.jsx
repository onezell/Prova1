import { useState, useEffect } from 'react'
import { Save, CheckCircle, Plus, Trash2, Edit3, X } from 'lucide-react'
import { getEmailSettings, updateEmailSettings, getAISettings, updateAISettings, getPollingSettings, updatePollingSettings, listMailboxes, createMailbox, updateMailbox, deleteMailbox } from '../api'

function Field({ label, value, onChange, type = 'text', placeholder = '' }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-600 mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full border rounded-lg px-3 py-2 text-sm"
      />
    </div>
  )
}

export default function SettingsPage() {
  const [emailConf, setEmailConf] = useState(null)
  const [aiConf, setAIConf] = useState(null)
  const [pollingConf, setPollingConf] = useState(null)
  const [saved, setSaved] = useState('')
  const [mboxes, setMboxes] = useState([])
  const [editingMbox, setEditingMbox] = useState(null)
  const [mboxForm, setMboxForm] = useState({ name: '', imap_host: '', imap_port: 993, imap_user: '', imap_password: '', smtp_host: '', smtp_port: 587, smtp_user: '', smtp_password: '', polling_enabled: true })

  const loadMailboxes = () => listMailboxes().then(({ data }) => setMboxes(data)).catch(() => {})

  useEffect(() => {
    getEmailSettings().then(({ data }) => setEmailConf(data))
    getAISettings().then(({ data }) => setAIConf(data))
    getPollingSettings().then(({ data }) => setPollingConf(data))
    loadMailboxes()
  }, [])

  const flash = (key) => { setSaved(key); setTimeout(() => setSaved(''), 2000) }

  const saveEmail = async () => { await updateEmailSettings(emailConf); flash('email') }
  const saveAI = async () => { await updateAISettings(aiConf); flash('ai') }
  const savePolling = async () => { await updatePollingSettings(pollingConf); flash('polling') }

  const updateEmail = (key, val) => setEmailConf((prev) => ({ ...prev, [key]: val }))
  const updateAI = (key, val) => setAIConf((prev) => ({ ...prev, [key]: val }))
  const updatePolling = (key, val) => setPollingConf((prev) => ({ ...prev, [key]: val }))
  const updateMboxForm = (key, val) => setMboxForm((prev) => ({ ...prev, [key]: val }))

  const resetMboxForm = () => {
    setEditingMbox(null)
    setMboxForm({ name: '', imap_host: '', imap_port: 993, imap_user: '', imap_password: '', smtp_host: '', smtp_port: 587, smtp_user: '', smtp_password: '', polling_enabled: true })
  }

  const saveMbox = async () => {
    try {
      if (editingMbox) {
        await updateMailbox(editingMbox, mboxForm)
      } else {
        await createMailbox(mboxForm)
      }
      resetMboxForm()
      loadMailboxes()
      flash('mailbox')
    } catch { /* empty */ }
  }

  const deleteMbox = async (id) => {
    if (!confirm('Eliminare questa casella?')) return
    await deleteMailbox(id)
    loadMailboxes()
  }

  const startEditMbox = (m) => {
    setEditingMbox(m.id)
    setMboxForm({ name: m.name, imap_host: m.imap_host, imap_port: m.imap_port, imap_user: m.imap_user, imap_password: '', smtp_host: m.smtp_host, smtp_port: m.smtp_port, smtp_user: m.smtp_user, smtp_password: '', polling_enabled: m.polling_enabled })
  }

  if (!emailConf || !aiConf || !pollingConf) return <div className="text-center py-12 text-gray-400">Caricamento...</div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-8">Impostazioni</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Email settings */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-lg font-semibold mb-4">Configurazione Email</h2>
          <div className="space-y-3">
            <Field label="IMAP Host" value={emailConf.imap_host} onChange={(v) => updateEmail('imap_host', v)} />
            <Field label="IMAP Port" value={emailConf.imap_port} onChange={(v) => updateEmail('imap_port', parseInt(v) || 0)} type="number" />
            <Field label="IMAP User" value={emailConf.imap_user} onChange={(v) => updateEmail('imap_user', v)} placeholder="email@example.com" />
            <Field label="IMAP Password" value={emailConf.imap_password} onChange={(v) => updateEmail('imap_password', v)} type="password" />
            <Field label="SMTP Host" value={emailConf.smtp_host} onChange={(v) => updateEmail('smtp_host', v)} />
            <Field label="SMTP Port" value={emailConf.smtp_port} onChange={(v) => updateEmail('smtp_port', parseInt(v) || 0)} type="number" />
            <Field label="SMTP User" value={emailConf.smtp_user} onChange={(v) => updateEmail('smtp_user', v)} placeholder="email@example.com" />
            <Field label="SMTP Password" value={emailConf.smtp_password} onChange={(v) => updateEmail('smtp_password', v)} type="password" />
          </div>
          <button onClick={saveEmail} className="mt-4 flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
            {saved === 'email' ? <CheckCircle className="h-4 w-4" /> : <Save className="h-4 w-4" />}
            {saved === 'email' ? 'Salvato!' : 'Salva'}
          </button>
        </div>

        {/* AI settings */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h2 className="text-lg font-semibold mb-4">Configurazione AI</h2>
          <div className="space-y-3">
            <Field label="API Key" value={aiConf.openai_api_key} onChange={(v) => updateAI('openai_api_key', v)} type="password" />
            <Field label="Base URL" value={aiConf.openai_base_url} onChange={(v) => updateAI('openai_base_url', v)} placeholder="https://api.openai.com/v1" />
            <Field label="Modello" value={aiConf.openai_model} onChange={(v) => updateAI('openai_model', v)} placeholder="gpt-4o-mini" />
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Categorie (una per riga)</label>
              <textarea
                value={aiConf.categories.join('\n')}
                onChange={(e) => updateAI('categories', e.target.value.split('\n').filter(Boolean))}
                rows={6}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
          </div>
          <button onClick={saveAI} className="mt-4 flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700">
            {saved === 'ai' ? <CheckCircle className="h-4 w-4" /> : <Save className="h-4 w-4" />}
            {saved === 'ai' ? 'Salvato!' : 'Salva'}
          </button>
        </div>

        {/* Polling settings */}
        <div className="bg-white rounded-xl shadow-sm border p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Polling e Automazione</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Polling automatico</label>
              <select
                value={pollingConf.polling_enabled ? 'true' : 'false'}
                onChange={(e) => updatePolling('polling_enabled', e.target.value === 'true')}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              >
                <option value="false">Disattivato</option>
                <option value="true">Attivato</option>
              </select>
            </div>
            <Field
              label="Intervallo polling (secondi)"
              value={pollingConf.polling_interval_seconds}
              onChange={(v) => updatePolling('polling_interval_seconds', parseInt(v) || 300)}
              type="number"
            />
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                Soglia auto-approvazione (0 = disattivata)
              </label>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={pollingConf.auto_approve_threshold}
                onChange={(e) => updatePolling('auto_approve_threshold', parseFloat(e.target.value) || 0)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
              <p className="text-xs text-gray-400 mt-1">Es. 0.9 = auto-approva se confidenza AI {'>'} 90%</p>
            </div>
          </div>
          <button onClick={savePolling} className="mt-4 flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
            {saved === 'polling' ? <CheckCircle className="h-4 w-4" /> : <Save className="h-4 w-4" />}
            {saved === 'polling' ? 'Salvato!' : 'Salva'}
          </button>
        </div>

        {/* Mailbox management */}
        <div className="bg-white rounded-xl shadow-sm border p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Caselle Email (Multi-mailbox)</h2>

          {mboxes.length > 0 && (
            <div className="mb-4 space-y-2">
              {mboxes.map((m) => (
                <div key={m.id} className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-3">
                  <div>
                    <span className="font-medium text-gray-800">{m.name}</span>
                    <span className="text-sm text-gray-500 ml-3">{m.imap_user} @ {m.imap_host}</span>
                    <span className={`ml-3 text-xs px-2 py-0.5 rounded-full ${m.polling_enabled ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600'}`}>
                      {m.polling_enabled ? 'Polling attivo' : 'Polling spento'}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => startEditMbox(m)} className="p-1.5 text-gray-500 hover:text-blue-600"><Edit3 className="h-4 w-4" /></button>
                    <button onClick={() => deleteMbox(m.id)} className="p-1.5 text-gray-500 hover:text-red-600"><Trash2 className="h-4 w-4" /></button>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="border rounded-lg p-4 bg-gray-50">
            <h3 className="text-sm font-medium text-gray-600 mb-3">
              {editingMbox ? 'Modifica casella' : 'Aggiungi nuova casella'}
              {editingMbox && <button onClick={resetMboxForm} className="ml-2 text-gray-400 hover:text-gray-600"><X className="h-4 w-4 inline" /></button>}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Field label="Nome" value={mboxForm.name} onChange={(v) => updateMboxForm('name', v)} placeholder="es. Info, Vendite..." />
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">Polling</label>
                <select value={mboxForm.polling_enabled ? 'true' : 'false'} onChange={(e) => updateMboxForm('polling_enabled', e.target.value === 'true')} className="w-full border rounded-lg px-3 py-2 text-sm">
                  <option value="true">Attivato</option>
                  <option value="false">Disattivato</option>
                </select>
              </div>
              <Field label="IMAP Host" value={mboxForm.imap_host} onChange={(v) => updateMboxForm('imap_host', v)} />
              <Field label="IMAP Port" value={mboxForm.imap_port} onChange={(v) => updateMboxForm('imap_port', parseInt(v) || 0)} type="number" />
              <Field label="IMAP User" value={mboxForm.imap_user} onChange={(v) => updateMboxForm('imap_user', v)} />
              <Field label="IMAP Password" value={mboxForm.imap_password} onChange={(v) => updateMboxForm('imap_password', v)} type="password" />
              <Field label="SMTP Host" value={mboxForm.smtp_host} onChange={(v) => updateMboxForm('smtp_host', v)} />
              <Field label="SMTP Port" value={mboxForm.smtp_port} onChange={(v) => updateMboxForm('smtp_port', parseInt(v) || 0)} type="number" />
              <Field label="SMTP User" value={mboxForm.smtp_user} onChange={(v) => updateMboxForm('smtp_user', v)} />
              <Field label="SMTP Password" value={mboxForm.smtp_password} onChange={(v) => updateMboxForm('smtp_password', v)} type="password" />
            </div>
            <button onClick={saveMbox} className="mt-4 flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              {saved === 'mailbox' ? <CheckCircle className="h-4 w-4" /> : editingMbox ? <Save className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              {saved === 'mailbox' ? 'Salvato!' : editingMbox ? 'Aggiorna' : 'Aggiungi'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
