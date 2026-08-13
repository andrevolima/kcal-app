import { apiRequest, ensureCsrfToken, setAccessToken } from '../../api/client'
import type { AuthUser, LoginCredentials, LoginResponse } from '../../types/auth'

export async function login(credentials: LoginCredentials) {
  await ensureCsrfToken()
  const result = await apiRequest<LoginResponse>('/api/v1/auth/login/', { method: 'POST', body: JSON.stringify(credentials) }, false)
  setAccessToken(result.access)
  return result.user
}
export const getCurrentUser = () => apiRequest<AuthUser>('/api/v1/auth/me/')
export async function logout() {
  await ensureCsrfToken()
  try { await apiRequest<void>('/api/v1/auth/logout/', { method: 'POST' }, false) }
  finally { setAccessToken(null) }
}
