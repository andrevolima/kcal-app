import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'
export function PrivateRoute() {
  const { status } = useAuth()
  if (status === 'loading') return <main className="page">Carregando...</main>
  return status === 'anonymous' ? <Navigate to="/login" replace /> : <Outlet />
}
