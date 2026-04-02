import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On 401, redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && window.location.pathname !== '/login') {
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const login = (username, password) =>
  api.post('/auth/login', { username, password })
export const getMe = () => api.get('/auth/me')

// Emails
export const fetchEmails = (limit = 50) => api.post(`/emails/fetch?limit=${limit}`)
export const listEmails = (params = {}) => api.get('/emails', { params })
export const getEmail = (id) => api.get(`/emails/${id}`)
export const classifyEmail = (id) => api.post(`/emails/${id}/classify`)
export const classifyAll = () => api.post('/emails/classify-all')
export const correctCategory = (id, category) => api.post(`/emails/${id}/correct`, { category })
export const sendReply = (id, replyText) => api.post(`/emails/${id}/reply`, { email_id: id, reply_text: replyText })
export const generateReply = (id, instructions = '') => api.post(`/emails/${id}/generate-reply?instructions=${encodeURIComponent(instructions)}`)

// Stats
export const getStats = () => api.get('/stats')

// Settings
export const getEmailSettings = () => api.get('/settings/email')
export const updateEmailSettings = (s) => api.put('/settings/email', s)
export const getAISettings = () => api.get('/settings/ai')
export const updateAISettings = (s) => api.put('/settings/ai', s)

export default api
