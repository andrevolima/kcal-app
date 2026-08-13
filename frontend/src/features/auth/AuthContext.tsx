import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { AuthUser, LoginCredentials } from '../../types/auth'
import { getCurrentUser, login as loginRequest, logout as logoutRequest } from './authApi'

type AuthStatus = 'loading' | 'authenticated' | 'anonymous'
interface AuthValue { status: AuthStatus; user: AuthUser | null; login: (value: LoginCredentials) => Promise<void>; logout: () => Promise<void> }
const AuthContext = createContext<AuthValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('loading')
  const [user, setUser] = useState<AuthUser | null>(null)
  useEffect(() => { getCurrentUser().then((value) => { setUser(value); setStatus('authenticated') }).catch(() => setStatus('anonymous')) }, [])
  const login = useCallback(async (value: LoginCredentials) => { const current = await loginRequest(value); setUser(current); setStatus('authenticated') }, [])
  const logout = useCallback(async () => { try { await logoutRequest() } finally { setUser(null); setStatus('anonymous') } }, [])
  const value = useMemo(() => ({ status, user, login, logout }), [status, user, login, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export function useAuth() { const value = useContext(AuthContext); if (!value) throw new Error('AuthProvider is required'); return value }
