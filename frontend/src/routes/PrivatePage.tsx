import { useAuth } from '../features/auth/AuthContext'
export function PrivatePage() {
  const { user, logout } = useAuth()
  return <main className="page"><section className="card">
    <span className="eyebrow">Área privada</span><h1>Autenticação confirmada.</h1><p>{user?.email}</p>
    <div className="status online"><span aria-hidden="true" />{user?.role}</div>
    <button type="button" onClick={() => void logout()}>Sair</button>
  </section></main>
}
