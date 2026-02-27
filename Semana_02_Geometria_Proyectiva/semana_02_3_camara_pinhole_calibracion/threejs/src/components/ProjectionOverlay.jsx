function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value))
}

export function ProjectionOverlay({ projectionData, distortionState }) {
  const { imageWidth, imageHeight, points } = projectionData

  return (
    <section className="projection-overlay">
      <header>
        <h2>Proyeccion 3D -{">"} 2D</h2>
        <p>Puntos turquesa = pinhole ideal. Puntos naranja = con distorsion radial.</p>
      </header>

      <svg viewBox={`0 0 ${imageWidth} ${imageHeight}`} role="img" aria-label="Proyeccion de puntos">
        <rect x="0" y="0" width={imageWidth} height={imageHeight} fill="#03101b" stroke="#195174" strokeWidth="3" />

        {Array.from({ length: 9 }, (_, index) => {
          const x = (imageWidth / 8) * index
          const y = (imageHeight / 8) * index

          return (
            <g key={`grid-${index}`}>
              <line x1={x} y1="0" x2={x} y2={imageHeight} stroke="#123049" strokeWidth="1" />
              <line x1="0" y1={y} x2={imageWidth} y2={y} stroke="#123049" strokeWidth="1" />
            </g>
          )
        })}

        <line
          x1={imageWidth * 0.5}
          y1="0"
          x2={imageWidth * 0.5}
          y2={imageHeight}
          stroke="#8bd3ff"
          strokeDasharray="8 6"
          strokeWidth="1.5"
        />
        <line
          x1="0"
          y1={imageHeight * 0.5}
          x2={imageWidth}
          y2={imageHeight * 0.5}
          stroke="#8bd3ff"
          strokeDasharray="8 6"
          strokeWidth="1.5"
        />

        {points.filter((point) => point.isInFront).map((point) => {
          const u = clamp(point.undistorted.u, -40, imageWidth + 40)
          const v = clamp(point.undistorted.v, -40, imageHeight + 40)
          const ud = clamp(point.distorted.u, -40, imageWidth + 40)
          const vd = clamp(point.distorted.v, -40, imageHeight + 40)
          const delta = Math.hypot(ud - u, vd - v)
          const labelX = (u + ud) * 0.5 + 9
          const labelY = (v + vd) * 0.5 - 8

          return (
            <g key={point.id}>
              <circle cx={u} cy={v} r="8" fill="#31d0e0" stroke="#d7f8fb" strokeWidth="1.6" opacity="0.92" />
              <text x={u + 10} y={v - 10} fill="#c5f6fa" fontSize="21">{point.label}</text>

              {distortionState.enabled ? (
                <>
                  <line x1={u} y1={v} x2={ud} y2={vd} stroke="#f08a24" strokeWidth="2.5" />
                  <circle cx={ud} cy={vd} r="8" fill="#f08a24" stroke="#ffe0c1" strokeWidth="1.5" opacity="0.95" />
                  <text x={labelX} y={labelY} fill="#ffd7ab" fontSize="17">d={delta.toFixed(1)}px</text>
                </>
              ) : null}
            </g>
          )
        })}
      </svg>

      <div className="projection-table">
        <div>
          <span className="legend swatch-cyan" />
          Proyeccion pinhole
        </div>
        <div>
          <span className="legend swatch-orange" />
          Proyeccion con k1/k2
        </div>
      </div>
    </section>
  )
}
