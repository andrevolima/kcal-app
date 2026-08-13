import { useEffect, useState } from 'react'
import { getApiStatus } from './api'
import './styles.css'

export default function App() {
  const [apiStatus, setApiStatus] = useState('Conectando ao backend...')
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    getApiStatus()
      .then(() => {
        setConnected(true)
        setApiStatus('Backend conectado')
      })
      .catch(() => setApiStatus('Backend indisponível'))
  }, [])

  return (
    <main className="page">
      <section className="card">
        <span className="eyebrow">Kcal</span>
        <h1>Seu projeto está pronto para começar.</h1>
        <p>
          O frontend React está configurado com Vite e integrado à API Django.
        </p>
        <div className={`status ${connected ? 'online' : ''}`}>
          <span aria-hidden="true" />
          {apiStatus}
        </div>
      </section>
    </main>
  )
}
