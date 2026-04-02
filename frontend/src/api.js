import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const fetchEmails = (limit = 50) => api.post(`/emails/fetch?limit=${limit}`)
export const listEmails = (status) => api.get('/emails', { params: status ? { status } : {} })
export const getEmail = (id) => api.get(`/emails/${id}`)
export const classifyEmail = (id) => api.post(`/emails/${id}/classify`)
export const classifyAll = () => api.post('/emails/classify-all')
export const sendReply = (id, replyText) => api.post(`/emails/${id}/reply`, { email_id: id, reply_text: replyText })
export const generateReply = (id, instructions = '') => api.post(`/emails/${id}/generate-reply?instructions=${encodeURIComponent(instructions)}`)
export const getStats = () => api.get('/stats')
export const getEmailSettings = () => api.get('/settings/email')
export const updateEmailSettings = (s) => api.put('/settings/email', s)
export const getAISettings = () => api.get('/settings/ai')
export const updateAISettings = (s) => api.put('/settings/ai', s)

export default api
