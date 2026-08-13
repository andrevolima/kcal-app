import { Navigate, Route, Routes } from 'react-router-dom'
import { LoginPage } from './features/auth/LoginPage'
import { PrivatePage } from './routes/PrivatePage'
import { PrivateRoute } from './routes/PrivateRoute'
import './styles.css'
export default function App() { return <Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route element={<PrivateRoute />}><Route path="/app" element={<PrivatePage />} /></Route>
  <Route path="*" element={<Navigate to="/app" replace />} />
</Routes> }
