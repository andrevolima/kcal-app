import { useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ApiError } from '../../api/client'
import type { InvitationStatus } from '../../types/athlete'
import { activateInvitation, validateInvitation } from './invitationApi'

type PageState = 'loading' | 'ready' | 'success' | 'error'

const reasonMessages: Record<string, string> = {
  invalid: 'Este convite não é válido.',
  expired: 'Este convite expirou. Solicite um novo convite.',
  used: 'Este convite já foi utilizado.',
  revoked: 'Este convite foi substituído ou revogado.',
}

export function ActivationPage() {
  const { token = '' } = useParams()
  const [state, setState] = useState<PageState>('loading')
  const [invitation, setInvitation] = useState<InvitationStatus | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    validateInvitation(token)
      .then((value) => {
        setInvitation(value)
        setState(value.valid ? 'ready' : 'error')
      })
      .catch((caught) => {
        if (caught instanceof ApiError && caught.status === 429) {
          setError('Muitas tentativas. Aguarde antes de tentar novamente.')
        } else setError('Não foi possível validar o convite.')
        setState('error')
      })
  }, [token])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setError('')
    try {
      await activateInvitation(
        token,
        String(form.get('password')),
        String(form.get('password_confirm')),
      )
      setState('success')
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 429) {
        setError('Muitas tentativas. Aguarde antes de tentar novamente.')
      } else setError('A senha não foi aceita. Revise os campos e tente novamente.')
    }
  }

  return <main className="page"><section className="card auth-card">
    <span className="eyebrow">Primeiro acesso</span>
    {state === 'loading' && <h1>Validando convite...</h1>}
    {state === 'error' && <><h1>Convite indisponível</h1><p role="alert">{error || reasonMessages[invitation?.reason ?? 'invalid']}</p></>}
    {state === 'ready' && <><h1>Crie sua senha</h1><p>Escolha uma senha segura para acessar o Kcalor.</p>
      <form onSubmit={submit}>
        <label htmlFor="password">Senha</label><input id="password" name="password" type="password" autoComplete="new-password" required />
        <label htmlFor="password-confirm">Confirmar senha</label><input id="password-confirm" name="password_confirm" type="password" autoComplete="new-password" required />
        {error && <p className="form-error" role="alert">{error}</p>}
        <button type="submit">Ativar conta</button>
      </form></>}
    {state === 'success' && <><h1>Conta ativada</h1><p>Sua senha foi definida. Agora você pode entrar normalmente.</p><Link className="link-action" to="/login">Ir para login</Link></>}
  </section></main>
}
