const API_URL = import.meta.env.VITE_API_URL ?? ''
interface ApiErrorPayload { error?: { message?: string; retry_after?: number } }

export class ApiError extends Error {
  constructor(public readonly status: number, message: string, public readonly retryAfter?: number) { super(message) }
}

let accessToken: string | null = null
let refreshPromise: Promise<string | null> | null = null
export function setAccessToken(token: string | null) { accessToken = token }

function getCookie(name: string) {
  const prefix = `${name}=`
  const cookie = document.cookie.split(';').map((value) => value.trim()).find((value) => value.startsWith(prefix))
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null
}

async function parseError(response: Response) {
  let payload: ApiErrorPayload = {}
  try { payload = (await response.json()) as ApiErrorPayload } catch { /* safe generic error */ }
  const headerRetry = response.headers.get('Retry-After')
  const retryAfter = payload.error?.retry_after ?? (headerRetry ? Number(headerRetry) : undefined)
  return new ApiError(response.status, payload.error?.message ?? 'Não foi possível concluir a solicitação.', retryAfter)
}

async function rawRequest(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers)
  if (init.body) headers.set('Content-Type', 'application/json')
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)
  const csrf = getCookie('csrftoken')
  if (csrf && init.method && init.method !== 'GET') headers.set('X-CSRFToken', csrf)
  return fetch(`${API_URL}${path}`, { ...init, headers, credentials: 'include' })
}

export async function ensureCsrfToken() {
  const response = await rawRequest('/api/v1/auth/csrf/')
  if (!response.ok) throw await parseError(response)
}

export async function refreshAccessToken(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      await ensureCsrfToken()
      const response = await rawRequest('/api/v1/auth/refresh/', { method: 'POST' })
      if (!response.ok) { setAccessToken(null); return null }
      const data = (await response.json()) as { access: string }
      setAccessToken(data.access)
      return data.access
    })().finally(() => { refreshPromise = null })
  }
  return refreshPromise
}

export async function apiRequest<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  let response = await rawRequest(path, init)
  if (response.status === 401 && retry) {
    if (await refreshAccessToken()) response = await rawRequest(path, init)
  }
  if (!response.ok) throw await parseError(response)
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}
