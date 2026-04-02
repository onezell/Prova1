import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

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
export const login = (username, password) => api.post('/auth/login', { username, password })
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

// Export
export const exportCSV = (params = {}) => api.get('/emails/export/csv', { params, responseType: 'blob' })

// Approval workflow
export const submitForApproval = (id, replyText) => api.post(`/emails/${id}/submit-for-approval`, { email_id: id, reply_text: replyText })
export const approveEmail = (id, replyText = null) => api.post(`/emails/${id}/approve`, replyText ? { reply_text: replyText } : {})
export const rejectEmail = (id) => api.post(`/emails/${id}/reject`)

// Templates
export const listTemplates = (category) => api.get('/templates', { params: category ? { category } : {} })
export const createTemplate = (data) => api.post('/templates', data)
export const getTemplate = (id) => api.get(`/templates/${id}`)
export const updateTemplate = (id, data) => api.put(`/templates/${id}`, data)
export const deleteTemplate = (id) => api.delete(`/templates/${id}`)

// Mailboxes
export const listMailboxes = () => api.get('/mailboxes')
export const createMailbox = (data) => api.post('/mailboxes', data)
export const updateMailbox = (id, data) => api.put(`/mailboxes/${id}`, data)
export const deleteMailbox = (id) => api.delete(`/mailboxes/${id}`)

// Stats
export const getStats = () => api.get('/stats')
export const getAccuracyStats = () => api.get('/stats/accuracy')

// Settings
export const getEmailSettings = () => api.get('/settings/email')
export const updateEmailSettings = (s) => api.put('/settings/email', s)
export const getAISettings = () => api.get('/settings/ai')
export const updateAISettings = (s) => api.put('/settings/ai', s)
export const getPollingSettings = () => api.get('/settings/polling')
export const updatePollingSettings = (s) => api.put('/settings/polling', s)

// Seed
export const seedData = () => api.post('/seed')

export default api
