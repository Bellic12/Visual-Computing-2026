const CHART_H = 150
const BAR_AREA_H = 110
const LABEL_H = 28
const PAD_L = 36
const PAD_R = 8

function barColor(pct) {
  if (pct <= 40) return '#3ac47d'
  if (pct <= 70) return '#e09040'
  return '#e05252'
}

export function OcupacionChart({ historial }) {
  if (!historial || historial.length < 2) {
    return (
      <div className="chart-placeholder" aria-label="Sin datos aún">
        <span>Sin datos aún — los valores se acumulan por hora durante la sesión</span>
      </div>
    )
  }

  const W = 100 // percent-based viewBox width
  const n = historial.length
  const gap = 0.15
  const barW = (W - PAD_L - PAD_R) / n * (1 - gap)
  const slotW = (W - PAD_L - PAD_R) / n

  // Y axis ticks: 0, 25, 50, 75, 100
  const ticks = [0, 25, 50, 75, 100]

  return (
    <svg
      viewBox={`0 0 ${W + PAD_L + PAD_R} ${CHART_H}`}
      preserveAspectRatio="none"
      className="chart-svg"
      aria-label="Gráfico de uso por hora"
      role="img"
    >
      {/* Y-axis grid lines & labels */}
      {ticks.map((t) => {
        const y = PAD_R + BAR_AREA_H - (t / 100) * BAR_AREA_H
        return (
          <g key={t}>
            <line
              x1={PAD_L}
              x2={W + PAD_L}
              y1={y}
              y2={y}
              stroke="rgba(255,255,255,0.09)"
              strokeWidth={0.4}
              strokeDasharray={t === 0 ? 'none' : '2 2'}
            />
            <text x={PAD_L - 3} y={y + 1} textAnchor="end" fontSize={5} fill="#507090">
              {t}%
            </text>
          </g>
        )
      })}

      {/* Bars */}
      {historial.map(({ hora, pct }, i) => {
        const barH = (pct / 100) * BAR_AREA_H
        const x = PAD_L + i * slotW + slotW * (gap / 2)
        const y = PAD_R + BAR_AREA_H - barH
        const color = barColor(pct)
        return (
          <g key={hora + i}>
            <rect
              x={x}
              y={y}
              width={barW}
              height={barH}
              fill={color}
              opacity={0.82}
              rx={1}
            />
            {/* Value label on bar */}
            {barH > 14 && (
              <text
                x={x + barW / 2}
                y={y + 9}
                textAnchor="middle"
                fontSize={4.5}
                fill="#fff"
                fontWeight="600"
              >
                {pct}%
              </text>
            )}
            {/* Hour label below bar */}
            <text
              x={x + barW / 2}
              y={PAD_R + BAR_AREA_H + LABEL_H * 0.55}
              textAnchor="middle"
              fontSize={4.5}
              fill="#507090"
            >
              {hora}
            </text>
          </g>
        )
      })}

      {/* Baseline */}
      <line
        x1={PAD_L}
        x2={W + PAD_L}
        y1={PAD_R + BAR_AREA_H}
        y2={PAD_R + BAR_AREA_H}
        stroke="rgba(255,255,255,0.12)"
        strokeWidth={0.6}
      />
    </svg>
  )
}
