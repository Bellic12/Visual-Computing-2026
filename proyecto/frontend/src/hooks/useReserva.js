import { useState, useCallback } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export function useReserva() {
  const [reserva, setReserva] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')

  const solicitar = useCallback(async (entrada) => {
    setCargando(true)
    setError('')
    try {
      const res = await fetch(`${API_BASE_URL}/reservar?entrada=${entrada}`, { method: 'POST' })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail ?? 'Error al reservar espacio')
        return
      }
      setReserva(data)
    } catch {
      setError('No se pudo conectar con el servidor')
    } finally {
      setCargando(false)
    }
  }, [])

  const liberar = useCallback(async () => {
    if (!reserva) return
    try {
      await fetch(`${API_BASE_URL}/reservar/${encodeURIComponent(reserva.espacio_id)}`, { method: 'DELETE' })
    } catch {
      // Reserva expira automáticamente en 60 segundos si no se libera
    }
    setReserva(null)
    setError('')
  }, [reserva])

  return { reserva, cargando, error, solicitar, liberar }
}
