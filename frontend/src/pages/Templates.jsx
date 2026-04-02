import { useState, useEffect } from 'react'
import { Plus, Pencil, Trash2, Save, X } from 'lucide-react'
import { listTemplates, createTemplate, updateTemplate, deleteTemplate } from '../api'
import CategoryBadge from '../components/CategoryBadge'

const CATEGORIES = ['richiesta_info', 'reclamo', 'supporto_tecnico', 'preventivo', 'collaborazione', 'spam', 'altro']

const emptyForm = { category: 'richiesta_info', title: '', body: '' }

export default function Templates() {
  const [templates, setTemplates] = useState([])
  const [editing, setEditing] = useState(null) // null | 'new' | template id
  const [form, setForm] = useState(emptyForm)
  const [message, setMessage] = useState('')

  const load = async () => {
    const { data } = await listTemplates()
    setTemplates(data)
  }

  useEffect(() => { load() }, [])

  const handleNew = () => {
    setEditing('new')
    setForm(emptyForm)
    setMessage('')
  }

  const handleEdit = (t) => {
    setEditing(t.id)
    setForm({ category: t.category, title: t.title, body: t.body })
    setMessage('')
  }

  const handleCancel = () => {
    setEditing(null)
    setForm(emptyForm)
  }

  const handleSave = async () => {
    try {
      if (editing === 'new') {
        await createTemplate(form)
        setMessage('Template creato')
      } else {
        await updateTemplate(editing, form)
        setMessage('Template aggiornato')
      }
      setEditing(null)
      setForm(emptyForm)
      await load()
    } catch (e) {
      setMessage(`Errore: ${e.response?.data?.detail || e.message}`)
    }
  }

  const handleDelete = async (id) => {
    try {
      await deleteTemplate(id)
      setMessage('Template eliminato')
      await load()
    } catch (e) {
      setMessage(`Errore: ${e.response?.data?.detail || e.message}`)
    }
  }

  const updateField = (key, val) => setForm((prev) => ({ ...prev, [key]: val }))

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Template Risposte</h1>
        <button onClick={handleNew} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
          <Plus className="h-4 w-4" /> Nuovo Template
        </button>
      </div>

      {message && (
        <div className="mb-4 p-3 bg-blue-50 text-blue-700 rounded-lg">{message}</div>
      )}

      {/* Editor */}
      {editing && (
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">{editing === 'new' ? 'Nuovo Template' : 'Modifica Template'}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Categoria</label>
              <select
                value={form.category}
                onChange={(e) => updateField('category', e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c.replace('_', ' ')}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Titolo</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => updateField('title', e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="es. Risposta standard reclamo"
              />
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-600 mb-1">
              Corpo (variabili: {'{{mittente}}'}, {'{{oggetto}}'}, {'{{categoria}}'})
            </label>
            <textarea
              value={form.body}
              onChange={(e) => updateField('body', e.target.value)}
              rows={8}
              className="w-full border rounded-lg px-3 py-2 text-sm resize-y"
              placeholder="Gentile {{mittente}},&#10;&#10;Grazie per averci contattato..."
            />
          </div>
          <div className="flex gap-2">
            <button onClick={handleSave} className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
              <Save className="h-4 w-4" /> Salva
            </button>
            <button onClick={handleCancel} className="flex items-center gap-2 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300">
              <X className="h-4 w-4" /> Annulla
            </button>
          </div>
        </div>
      )}

      {/* List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.length === 0 && !editing ? (
          <div className="col-span-full text-center py-12 text-gray-400">
            Nessun template. Crea il primo!
          </div>
        ) : (
          templates.map((t) => (
            <div key={t.id} className="bg-white rounded-xl shadow-sm border p-5">
              <div className="flex items-center justify-between mb-2">
                <CategoryBadge category={t.category} />
                <div className="flex gap-1">
                  <button onClick={() => handleEdit(t)} className="p-1 text-gray-400 hover:text-blue-600">
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button onClick={() => handleDelete(t.id)} className="p-1 text-gray-400 hover:text-red-600">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <h3 className="font-medium text-gray-800 mb-2">{t.title}</h3>
              <p className="text-sm text-gray-500 line-clamp-3">{t.body}</p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
