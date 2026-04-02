import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, LogIn } from 'lucide-react'
import { login } from '../api'

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await login(username, password)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('refreshToken', data.refresh_token)
      onLogin(username)
      navigate('/')
    } catch {
      setError('Credenziali non valide')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-sm">
        <div className="text-center mb-6">
          <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-3">
            <Mail className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-xl font-bold text-gray-800">Email AI Classifier</h1>
          <p className="text-sm text-gray-500 mt-1">Accedi per continuare</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
              required
              autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <LogIn className="h-4 w-4" />
            {loading ? 'Accesso...' : 'Accedi'}
          </button>
        </form>
      </div>
    </div>
  )
}
