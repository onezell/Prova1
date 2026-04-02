import { useState, useEffect } from 'react'
import { Save, CheckCircle } from 'lucide-react'
import { getEmailSettings, updateEmailSettings, getAISettings, updateAISettings } from '../api'

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
  const [saved, setSaved] = useState('')

  useEffect(() => {
    getEmailSettings().then(({ data }) => setEmailConf(data))
    getAISettings().then(({ data }) => setAIConf(data))
  }, [])

  const saveEmail = async () => {
    await updateEmailSettings(emailConf)
    setSaved('email')
    setTimeout(() => setSaved(''), 2000)
  }

  const saveAI = async () => {
    await updateAISettings(aiConf)
    setSaved('ai')
    setTimeout(() => setSaved(''), 2000)
  }

  const updateEmail = (key, val) => setEmailConf((prev) => ({ ...prev, [key]: val }))
  const updateAI = (key, val) => setAIConf((prev) => ({ ...prev, [key]: val }))

  if (!emailConf || !aiConf) return <div className="text-center py-12 text-gray-400">Caricamento...</div>

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
      </div>
    </div>
  )
}
