import { useEffect, useMemo, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export function useEspacios() {
  const [espacios, setEspacios] = useState([])
  const [ruta, setRuta] = useState([])
  const [destino, setDestino] = useState(null)
  const [entrada, setEntrada] = useState('noroeste')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [updatedAt, setUpdatedAt] = useState(null)

  useEffect(() => {
    let active = true
    const eventSource = new EventSource(`${API_BASE_URL}/suscripcion/estado?entrada=${entrada}`)

    eventSource.addEventListener('estado', (event) => {
      if (!active) {
        return
      }

      try {
        const payload = JSON.parse(event.data)

        if (!payload || !Array.isArray(payload.espacios)) {
          throw new Error('Respuesta invalida de /suscripcion/estado')
        }

        setEspacios(payload.espacios)
        setRuta(Array.isArray(payload.ruta) ? payload.ruta : [])
        setDestino(payload.destino ?? null)
        setEntrada(payload.entrada ?? entrada)
        setError('')
        setUpdatedAt(new Date())
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'No se pudo procesar el evento')
      }
    })

    eventSource.onerror = () => {
      if (!active) {
        return
      }

      setError('La suscripcion al parqueadero se interrumpio')
      setLoading(false)
    }

    return () => {
      active = false
      eventSource.close()
    }
  }, [entrada])

  const stats = useMemo(() => {
    const total = espacios.length
    const ocupados = espacios.filter((e) => e.ocupado).length
    const libres = Math.max(0, total - ocupados)
    const ocupacion = total > 0 ? Math.round((ocupados / total) * 100) : 0

    return { total, ocupados, libres, ocupacion }
  }, [espacios])

  return { espacios, ruta, destino, entrada, stats, loading, error, updatedAt }
}
