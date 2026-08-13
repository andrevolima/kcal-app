import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from '../../App'
import { ApiError } from '../../api/client'
import { AuthProvider } from '../auth/AuthContext'
import * as authApi from '../auth/authApi'
import * as invitationApi from './invitationApi'

vi.mock('../auth/authApi')
vi.mock('./invitationApi')

const nutritionist = { id: 1, email: 'nutritionist@example.com', role: 'nutritionist' as const }
const athlete = {
  id: 7,
  email: 'athlete@example.com',
  first_name: 'Ana',
  last_name: 'Runner',
  is_active: true,
  onboarding_status: 'not_invited' as const,
}

function renderApp(path: string) {
  return render(<MemoryRouter initialEntries={[path]}><AuthProvider><App /></AuthProvider></MemoryRouter>)
}

describe('athlete invitation onboarding', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    vi.mocked(authApi.getCurrentUser).mockRejectedValue(new Error())
  })

  it('shows a valid invitation and password form', async () => {
    vi.mocked(invitationApi.validateInvitation).mockResolvedValue({ valid: true, expires_at: '2026-08-14T00:00:00Z' })
    renderApp('/activate/token')
    expect(await screen.findByRole('heading', { name: 'Crie sua senha' })).toBeInTheDocument()
    expect(screen.getByLabelText('Confirmar senha')).toBeInTheDocument()
  })

  it.each([
    ['invalid', 'não é válido'],
    ['expired', 'expirou'],
    ['used', 'já foi utilizado'],
  ] as const)('shows the %s invitation state', async (reason, message) => {
    vi.mocked(invitationApi.validateInvitation).mockResolvedValue({ valid: false, reason })
    renderApp('/activate/token')
    expect(await screen.findByRole('alert')).toHaveTextContent(message)
  })

  it('shows rejected password feedback', async () => {
    vi.mocked(invitationApi.validateInvitation).mockResolvedValue({ valid: true })
    vi.mocked(invitationApi.activateInvitation).mockRejectedValue(new ApiError(400, 'invalid'))
    renderApp('/activate/token')
    await userEvent.type(await screen.findByLabelText('Senha'), 'weak')
    await userEvent.type(screen.getByLabelText('Confirmar senha'), 'weak')
    fireEvent.click(screen.getByRole('button', { name: 'Ativar conta' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('senha não foi aceita')
  })

  it('handles HTTP 429', async () => {
    vi.mocked(invitationApi.validateInvitation).mockResolvedValue({ valid: true })
    vi.mocked(invitationApi.activateInvitation).mockRejectedValue(new ApiError(429, 'limited'))
    renderApp('/activate/token')
    await userEvent.type(await screen.findByLabelText('Senha'), 'password')
    await userEvent.type(screen.getByLabelText('Confirmar senha'), 'password')
    fireEvent.click(screen.getByRole('button', { name: 'Ativar conta' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Muitas tentativas')
  })

  it('activates and navigates to login', async () => {
    vi.mocked(invitationApi.validateInvitation).mockResolvedValue({ valid: true })
    vi.mocked(invitationApi.activateInvitation).mockResolvedValue({ activated: true })
    renderApp('/activate/token')
    await userEvent.type(await screen.findByLabelText('Senha'), 'strong-password')
    await userEvent.type(screen.getByLabelText('Confirmar senha'), 'strong-password')
    fireEvent.click(screen.getByRole('button', { name: 'Ativar conta' }))
    fireEvent.click(await screen.findByRole('link', { name: 'Ir para login' }))
    expect(await screen.findByRole('heading', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('lets a nutritionist generate and regenerate invitations', async () => {
    vi.mocked(authApi.getCurrentUser).mockResolvedValue(nutritionist)
    vi.mocked(invitationApi.getAthlete).mockResolvedValue(athlete)
    vi.mocked(invitationApi.issueInvitation).mockResolvedValue({ status: 'pending', expires_at: '2026-08-14T00:00:00Z', invitation_url: 'http://localhost:5173/activate/token' })
    renderApp('/athletes/7')
    fireEvent.click(await screen.findByRole('button', { name: 'Gerar convite' }))
    expect(await screen.findByText('Convite gerado com sucesso.')).toBeInTheDocument()
    expect(screen.getByText('http://localhost:5173/activate/token')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Gerar novo convite' })).toBeInTheDocument()
  })
})
