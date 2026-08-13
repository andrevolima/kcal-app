import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { ApiError } from '../../api/client'
import type { Athlete } from '../../types/athlete'
import { getAthlete, issueInvitation } from './invitationApi'

export function AthleteInvitationPage() {
  const { id = '' } = useParams()
  const [athlete, setAthlete] = useState<Athlete | null>(null)
  const [link, setLink] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => { getAthlete(id).then(setAthlete).catch(() => setMessage('Não foi possível carregar o atleta.')) }, [id])

  async function invite() {
    setMessage('')
    try {
      const result = await issueInvitation(id)
      setLink(result.invitation_url ?? '')
      setAthlete((current) => current ? { ...current, onboarding_status: 'pending' } : current)
      setMessage('Convite gerado com sucesso.')
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 429) setMessage('Limite de convites atingido. Tente mais tarde.')
      else setMessage('Não foi possível gerar o convite.')
    }
  }

  return <main className="page"><section className="card">
    <span className="eyebrow">Atleta</span><h1>{athlete ? `${athlete.first_name} ${athlete.last_name}`.trim() || athlete.email : 'Carregando...'}</h1>
    {athlete && <><p>{athlete.email}</p><div className="status"><span aria-hidden="true" />Onboarding: {athlete.onboarding_status}</div>
      {athlete.onboarding_status !== 'activated' && <button type="button" onClick={() => void invite()}>{athlete.onboarding_status === 'pending' ? 'Gerar novo convite' : 'Gerar convite'}</button>}
    </>}
    {message && <p role="status">{message}</p>}
    {link && <div className="development-link"><strong>Link de desenvolvimento</strong><code>{link}</code></div>}
  </section></main>
}
