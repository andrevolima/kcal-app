import { useState, type FormEvent } from 'react'
import { Navigate } from 'react-router-dom'
import { ApiError } from '../../api/client'
import { useAuth } from './AuthContext'

export function LoginPage() {
  const { status, login } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  if (status === 'authenticated') return <Navigate to="/app" replace />

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setLoading(true); setError('')
    try { await login({ email: String(form.get('email')), password: String(form.get('password')) }) }
    catch (caught) {
      if (caught instanceof ApiError && caught.status === 429) setError(`Muitas tentativas de acesso.${caught.retryAfter ? ` Tente novamente em ${caught.retryAfter}s.` : ''}`)
      else if (caught instanceof ApiError && caught.status === 401) setError('E-mail ou senha inválidos.')
      else setError('Não foi possível entrar. Tente novamente.')
    } finally { setLoading(false) }
  }

  return <main className="page"><section className="card auth-card">
    <span className="eyebrow">PPN</span><h1>Entrar</h1><p>Acesse sua área de acompanhamento nutricional.</p>
    <form onSubmit={submit}>
      <label htmlFor="email">E-mail</label><input id="email" name="email" type="email" autoComplete="email" required />
      <label htmlFor="password">Senha</label><input id="password" name="password" type="password" autoComplete="current-password" required />
      {error && <p className="form-error" role="alert">{error}</p>}
      <button type="submit" disabled={loading}>{loading ? 'Entrando...' : 'Entrar'}</button>
    </form>
  </section></main>
}
