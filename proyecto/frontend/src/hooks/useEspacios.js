import { useEffect, useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export function useEspacios(pollMs = 5000) {
  const [espacios, setEspacios] = useState([])
  const [ruta, setRuta] = useState([])
  const [destino, setDestino] = useState(null)
  const [entrada, setEntrada] = useState('noroeste')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [updatedAt, setUpdatedAt] = useState(null)

  useEffect(() => {
    let active = true

    const fetchEspacios = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/estado?entrada=${entrada}`)
        if (!response.ok) {
          throw new Error(`Error ${response.status}`)
        }

        const payload = await response.json()
        if (!payload || !Array.isArray(payload.espacios)) {
          throw new Error('Respuesta invalida de /estado')
        }

        if (active) {
          setEspacios(payload.espacios)
          setRuta(Array.isArray(payload.ruta) ? payload.ruta : [])
          setDestino(payload.destino ?? null)
          setEntrada(payload.entrada ?? entrada)
          setError('')
          setUpdatedAt(new Date())
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : 'No se pudo cargar /estado')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    fetchEspacios()
    const timer = setInterval(fetchEspacios, pollMs)

    return () => {
      active = false
      clearInterval(timer)
    }
  }, [pollMs])

  const stats = useMemo(() => {
    const total = espacios.length
    const ocupados = espacios.filter((e) => e.ocupado).length
    const libres = Math.max(0, total - ocupados)
    const ocupacion = total > 0 ? Math.round((ocupados / total) * 100) : 0

    return { total, ocupados, libres, ocupacion }
  }, [espacios])

  return { espacios, ruta, destino, entrada, stats, loading, error, updatedAt }
}
