const API_URL = import.meta.env.VITE_API_URL ?? ''

export async function getApiStatus() {
  const response = await fetch(`${API_URL}/api/health/`)

  if (!response.ok) {
    throw new Error(`A API respondeu com o status ${response.status}`)
  }

  return response.json()
}
