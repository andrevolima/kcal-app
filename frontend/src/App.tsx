import { Navigate, Route, Routes } from 'react-router-dom'
import { LoginPage } from './features/auth/LoginPage'
import { ActivationPage } from './features/athletes/ActivationPage'
import { AthleteInvitationPage } from './features/athletes/AthleteInvitationPage'
import { PrivatePage } from './routes/PrivatePage'
import { PrivateRoute } from './routes/PrivateRoute'
import './styles.css'
export default function App() { return <Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route path="/activate/:token" element={<ActivationPage />} />
  <Route element={<PrivateRoute />}><Route path="/app" element={<PrivatePage />} /><Route path="/athletes/:id" element={<AthleteInvitationPage />} /></Route>
  <Route path="*" element={<Navigate to="/app" replace />} />
</Routes> }
