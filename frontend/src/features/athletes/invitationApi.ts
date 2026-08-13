import { apiRequest, ensureCsrfToken } from '../../api/client'
import type {
  Athlete,
  InvitationIssue,
  InvitationStatus,
} from '../../types/athlete'

export const getAthlete = (id: string) =>
  apiRequest<Athlete>(`/api/v1/athletes/${id}/`)

export const issueInvitation = (id: string) =>
  apiRequest<InvitationIssue>(`/api/v1/athletes/${id}/invite/`, {
    method: 'POST',
  })

export const validateInvitation = (token: string) =>
  apiRequest<InvitationStatus>(`/api/v1/auth/invitations/${token}/`, {}, false)

export async function activateInvitation(
  token: string,
  password: string,
  passwordConfirm: string,
) {
  await ensureCsrfToken()
  return apiRequest<{ activated: true }>(
    `/api/v1/auth/invitations/${token}/activate/`,
    {
      method: 'POST',
      body: JSON.stringify({ password, password_confirm: passwordConfirm }),
    },
    false,
  )
}
