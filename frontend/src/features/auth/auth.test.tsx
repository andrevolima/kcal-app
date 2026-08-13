import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../../App'
import { ApiError } from '../../api/client'
import { AuthProvider } from './AuthContext'
import * as authApi from './authApi'

vi.mock('./authApi')
const user = { id: 1, email: 'user@example.com', role: 'nutritionist' as const }

function renderApp(path = '/login') {
  return render(<MemoryRouter initialEntries={[path]}><AuthProvider><App /></AuthProvider></MemoryRouter>)
}

describe('authentication flow', () => {
  beforeEach(() => vi.resetAllMocks())

  it('renders and submits login successfully', async () => {
    vi.mocked(authApi.getCurrentUser).mockRejectedValue(new Error())
    vi.mocked(authApi.login).mockResolvedValue(user)
    renderApp()
    await userEvent.type(screen.getByLabelText('E-mail'), user.email)
    await userEvent.type(screen.getByLabelText('Senha'), 'password')
    fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByText('Autenticação confirmada.')).toBeInTheDocument()
    expect(authApi.login).toHaveBeenCalledWith({ email: user.email, password: 'password' })
  })

  it('shows generic invalid credentials error', async () => {
    vi.mocked(authApi.getCurrentUser).mockRejectedValue(new Error())
    vi.mocked(authApi.login).mockRejectedValue(new ApiError(401, 'generic'))
    renderApp()
    await userEvent.type(screen.getByLabelText('E-mail'), user.email)
    await userEvent.type(screen.getByLabelText('Senha'), 'wrong')
    fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('E-mail ou senha inválidos.')
  })

  it('handles rate limiting and Retry-After', async () => {
    vi.mocked(authApi.getCurrentUser).mockRejectedValue(new Error())
    vi.mocked(authApi.login).mockRejectedValue(new ApiError(429, 'limited', 30))
    renderApp()
    await userEvent.type(screen.getByLabelText('E-mail'), user.email)
    await userEvent.type(screen.getByLabelText('Senha'), 'wrong')
    fireEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Tente novamente em 30s')
  })

  it('loads current user into a protected route', async () => {
    vi.mocked(authApi.getCurrentUser).mockResolvedValue(user)
    renderApp('/app')
    expect(await screen.findByText(user.email)).toBeInTheDocument()
    expect(screen.getByText('nutritionist')).toBeInTheDocument()
  })

  it('redirects anonymous visitors to login', async () => {
    vi.mocked(authApi.getCurrentUser).mockRejectedValue(new Error())
    renderApp('/app')
    expect(await screen.findByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('logs out through backend and returns to login', async () => {
    vi.mocked(authApi.getCurrentUser).mockResolvedValue(user)
    vi.mocked(authApi.logout).mockResolvedValue()
    renderApp('/app')
    fireEvent.click(await screen.findByRole('button', { name: 'Sair' }))
    await waitFor(() => expect(authApi.logout).toHaveBeenCalled())
    expect(await screen.findByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
  })
})
