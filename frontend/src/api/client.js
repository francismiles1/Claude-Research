/**
 * API client — Axios instance for backend communication.
 * Vite dev server proxies /api to FastAPI on :8000.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

export default api
