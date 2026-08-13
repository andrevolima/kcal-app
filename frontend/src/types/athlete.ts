export type OnboardingStatus = 'not_invited' | 'pending' | 'activated'

export interface Athlete {
  id: number
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  onboarding_status: OnboardingStatus
}

export interface InvitationStatus {
  valid: boolean
  expires_at?: string
  reason?: 'invalid' | 'expired' | 'used' | 'revoked'
}

export interface InvitationIssue {
  status: 'pending'
  expires_at: string
  invitation_url?: string
}
