import { useEffect, useState } from 'react'

/**
 * Tracks in-session occupancy bucketed by clock-hour.
 * Returns an array of up to 12 { hora: 'HH:MM', pct: number } entries.
 */
export function useHistorialOcupacion(stats) {
  const [historial, setHistorial] = useState([])

  useEffect(() => {
    if (stats.total === 0) return

    const hora = new Date()
      .toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', hour12: false })
      .slice(0, 5)

    setHistorial((prev) => {
      const last = prev.at(-1)
      if (last?.hora === hora) {
        // Running average within the same hour-bucket
        const updated = { hora, pct: Math.round((last.pct + stats.ocupacion) / 2) }
        return [...prev.slice(0, -1), updated]
      }
      return [...prev, { hora, pct: stats.ocupacion }].slice(-12)
    })
  }, [stats.ocupacion, stats.total])

  return historial
}
