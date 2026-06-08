import { useMemo, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Environment, MapControls, Sky, Line } from '@react-three/drei'
import * as THREE from 'three'

// ---------------------------------------------------------------------------
// Lot geometry  (all distances in metres, top-left origin)
// ---------------------------------------------------------------------------
const LOT_W   = 76
const LOT_H   = 13.5
const OX      = -LOT_W / 2   // −38
const OZ      = -LOT_H / 2   // −6.75

const STALL_W  = 2.4
const STALL_D  = 4.5
const LAMP_GAP = 1.6   // gap between col 14 and col 15 — concrete median
// MARGIN = 0: stalls run flush to the curb face (no gap between curb and stall)
const AISLE_W  = LOT_H - 2 * STALL_D   // 4.5 m two-way aisle

const AISLE_N_TL = STALL_D                  // 4.5
const AISLE_S_TL = STALL_D + AISLE_W        // 9.0
const ROW1_Z_TL  = STALL_D / 2              // 2.25
const ROW2_Z_TL  = AISLE_S_TL + STALL_D / 2 // 11.25

const AISLE_N = AISLE_N_TL + OZ   // −2.25
const AISLE_S = AISLE_S_TL + OZ   // +2.25

// Two concrete islands — one per parking row — with the central aisle left
// OPEN between them so cars can cross (like a street median with a break).
// Each island matches its row's depth (STALL_D) and runs curb → aisle edge.
const ISLAND_LEN = STALL_D                    // 4.5 m — same depth as a stall
const ISLAND_N_Z = ROW1_Z_TL + OZ             // −4.5  north island centre
const ISLAND_S_Z = ROW2_Z_TL + OZ             // +4.5  south island centre
const ISLAND_H   = 0.07                        // raised concrete height

// Two INDEPENDENT landscaped islands — one wrapping each row. Each is a U /
// bracket shape: a back strip behind the row plus two arms that wrap around
// the row's end slots and reach toward the aisle. The U opens to the central
// aisle, so the driveway stays clear (cars pass through the middle and reach
// the stalls) and the two islands never meet across the central road. Each is
// enclosed by its own unbroken curb, with rounded — but fairly sharp — corners.
const ISL_ARM_W  = 2.0     // width of each end-wrap arm (X) and back-strip depth (Z)
const ISL_CURB_W = 0.20    // visible concrete rim width
const ISL_CURB_H = 0.13    // raised curb height
const ISL_CORNER = 0.6     // corner fillet radius (small → fairly sharp corners)

// Structural gap X (centred) — where the concrete islands and lamp live
const LAMP_X = 14 * STALL_W + LAMP_GAP / 2 + OX     // ≈ −3.6

// Lamp post sits on the SOUTH island, at its aisle-facing edge, so the arm
// reaches OVER the central aisle and the lamp lights the street, not the slots.
const POLE_Z      = ISLAND_S_Z - ISLAND_LEN / 2 + 0.35   // ≈ +2.6  (aisle edge)
const POLE_BASE_H = 0.12
const COLLAR_H    = 0.13
const SHAFT_H     = 4.8
const POLE_TOP_Y  = POLE_BASE_H + COLLAR_H + SHAFT_H  // ≈ 5.05
const ARM_L       = 2.5   // reaches across to the aisle centre (lamp at Z ≈ 0)

// ---------------------------------------------------------------------------
// Static 62-space layout
// ---------------------------------------------------------------------------
function generarEspaciosEstaticos() {
  const rightXStart = 14 * STALL_W + LAMP_GAP
  const espacios = []
  for (const row of [1, 2]) {
    const zTL = row === 1 ? ROW1_Z_TL : ROW2_Z_TL
    for (let col = 1; col <= 14; col++) {
      espacios.push({ id: `E-${row}-${col}`, x: (col - 1) * STALL_W + STALL_W / 2, z: zTL })
    }
    for (let col = 15; col <= 31; col++) {
      const x = rightXStart + (col - 15) * STALL_W + STALL_W / 2
      espacios.push({ id: `E-${row}-${col}`, x, z: zTL })
    }
  }
  return espacios
}

const ESPACIOS_ESTATICOS = generarEspaciosEstaticos()

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
const PALETA = ['#2c3e50', '#5d4037', '#1a3a2a', '#4a3728', '#263238', '#37474f', '#4e342e', '#1b3a4b']

function hashCode(str) {
  let h = 0
  for (let i = 0; i < str.length; i++) h = (Math.imul(31, h) + str.charCodeAt(i)) | 0
  return h
}

function seededRand(seed) {
  const x = Math.sin(seed + 1) * 10000
  return x - Math.floor(x)
}

// Build a closed Shape from a list of [x, y] points, filleting every corner
// with radius r (quadratic rounding). Small r → fairly sharp corners. Works for
// concave shapes like the U-shaped islands.
function roundedPolygonShape(pts, r) {
  const s = new THREE.Shape()
  const n = pts.length
  for (let i = 0; i < n; i++) {
    const prev = pts[(i - 1 + n) % n]
    const curr = pts[i]
    const next = pts[(i + 1) % n]
    const v1x = prev[0] - curr[0], v1y = prev[1] - curr[1]
    const v2x = next[0] - curr[0], v2y = next[1] - curr[1]
    const l1 = Math.hypot(v1x, v1y) || 1
    const l2 = Math.hypot(v2x, v2y) || 1
    const r1 = Math.min(r, l1 / 2), r2 = Math.min(r, l2 / 2)
    const p1x = curr[0] + (v1x / l1) * r1, p1y = curr[1] + (v1y / l1) * r1
    const p2x = curr[0] + (v2x / l2) * r2, p2y = curr[1] + (v2y / l2) * r2
    if (i === 0) s.moveTo(p1x, p1y)
    else s.lineTo(p1x, p1y)
    s.quadraticCurveTo(curr[0], curr[1], p2x, p2y)
  }
  s.closePath()
  return s
}

// ---------------------------------------------------------------------------
// Textures
// ---------------------------------------------------------------------------
function crearTexturaAsfalto() {
  const W = 2048, H = 512
  const canvas = document.createElement('canvas')
  canvas.width = W; canvas.height = H
  const ctx = canvas.getContext('2d')

  ctx.fillStyle = '#3c3a37'
  ctx.fillRect(0, 0, W, H)

  for (let i = 0; i < 16; i++) {
    const gx = seededRand(i * 3) * W
    const gy = seededRand(i * 3 + 1) * H
    const r  = 160 + seededRand(i * 3 + 2) * 300
    const gr = ctx.createRadialGradient(gx, gy, 0, gx, gy, r)
    const v  = seededRand(i * 7) > 0.5 ? 9 : -5
    const b  = 60 + v
    gr.addColorStop(0, `rgba(${b},${b - 2},${b - 3},0.18)`)
    gr.addColorStop(1, 'rgba(0,0,0,0)')
    ctx.fillStyle = gr
    ctx.fillRect(0, 0, W, H)
  }
  for (let i = 0; i < 10000; i++) {
    const x  = seededRand(i * 5) * W
    const y  = seededRand(i * 5 + 1) * H
    const sz = seededRand(i * 5 + 2) * 2.5 + 0.3
    const c  = 55 + Math.floor(seededRand(i * 5 + 3) * 20 - 8)
    ctx.fillStyle = `rgba(${c},${c - 1},${c - 2},0.18)`
    ctx.fillRect(x, y, sz, sz * 0.28)
  }
  for (let i = 0; i < 22; i++) {
    const y   = seededRand(i * 11) * H
    const len = 90 + seededRand(i * 11 + 1) * 480
    const x0  = seededRand(i * 11 + 2) * (W - len)
    const op  = 0.08 + seededRand(i * 11 + 3) * 0.12
    ctx.strokeStyle = `rgba(68,60,50,${op})`
    ctx.lineWidth = seededRand(i * 11 + 4) * 2.0 + 0.4
    ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x0 + len, y); ctx.stroke()
  }
  for (let i = 0; i < 10; i++) {
    const sx = seededRand(i * 17) * W
    const sy = seededRand(i * 17 + 1) * H
    const sr = ctx.createRadialGradient(sx, sy, 0, sx, sy, 13 + seededRand(i * 17 + 2) * 16)
    sr.addColorStop(0, 'rgba(20,16,12,0.26)')
    sr.addColorStop(1, 'rgba(0,0,0,0)')
    ctx.fillStyle = sr
    ctx.beginPath()
    ctx.ellipse(sx, sy, 18 + seededRand(i * 17 + 3) * 14, 9 + seededRand(i * 17 + 4) * 7, 0, 0, Math.PI * 2)
    ctx.fill()
  }

  const tex = new THREE.CanvasTexture(canvas)
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping
  tex.repeat.set(8, 2)
  return tex
}

// Alpha map: opaque centre, soft fade only at the FAR outer perimeter (all 4
// edges). Keeps the apron solid near the lot, dissolving gently into the horizon.
function crearAlphaFadeBorde() {
  const S = 256
  const canvas = document.createElement('canvas')
  canvas.width = S; canvas.height = S
  const ctx = canvas.getContext('2d')

  ctx.fillStyle = '#fff'
  ctx.fillRect(0, 0, S, S)

  ctx.globalCompositeOperation = 'multiply'
  const f = 0.14   // fade fraction at each edge

  let g = ctx.createLinearGradient(0, 0, S * f, 0)
  g.addColorStop(0, '#000'); g.addColorStop(1, '#fff')
  ctx.fillStyle = g; ctx.fillRect(0, 0, S * f, S)
  g = ctx.createLinearGradient(S * (1 - f), 0, S, 0)
  g.addColorStop(0, '#fff'); g.addColorStop(1, '#000')
  ctx.fillStyle = g; ctx.fillRect(S * (1 - f), 0, S * f, S)
  g = ctx.createLinearGradient(0, 0, 0, S * f)
  g.addColorStop(0, '#000'); g.addColorStop(1, '#fff')
  ctx.fillStyle = g; ctx.fillRect(0, 0, S, S * f)
  g = ctx.createLinearGradient(0, S * (1 - f), 0, S)
  g.addColorStop(0, '#fff'); g.addColorStop(1, '#000')
  ctx.fillStyle = g; ctx.fillRect(0, S * (1 - f), S, S * f)

  return new THREE.CanvasTexture(canvas)
}

// ---------------------------------------------------------------------------
// Scene components
// ---------------------------------------------------------------------------

function Piso() {
  const tex = useMemo(() => crearTexturaAsfalto(), [])
  return (
    <mesh rotation-x={-Math.PI / 2} position={[0, -0.02, 0]} receiveShadow>
      <planeGeometry args={[LOT_W, LOT_H]} />
      <meshStandardMaterial map={tex} roughness={0.92} metalness={0.01} />
    </mesh>
  )
}

// Asphalt apron surrounding the lot — everything outside the landscaped island
// ring is paved. Fades at the far edges so the scene never looks cut off.
function Entorno() {
  const fade = useMemo(() => crearAlphaFadeBorde(), [])
  return (
    <mesh rotation-x={-Math.PI / 2} position={[0, -0.035, 0]} receiveShadow>
      <planeGeometry args={[LOT_W + 80, LOT_H + 80]} />
      <meshStandardMaterial color="#3c3a37" roughness={0.93} metalness={0.02} alphaMap={fade} transparent />
    </mesh>
  )
}

// U-shaped outline (in the shape's XY plane) for one island: a back strip
// behind a row plus two arms wrapping the row's end slots, opening toward the
// aisle. `g` (±1) mirrors it for the two rows; `d` erodes it inward (used for
// the curb's inner hole and the grass fill). Points go: outer rectangle, then
// in across an arm tip and around the central notch (the row / opening).
function islaUPoints(g, d) {
  const XO = (LOT_W / 2 + ISL_ARM_W) - d        // arm outer X        (±40)
  const XI = (LOT_W / 2) + d                      // notch (row) side X (±38)
  const zF = g * ((LOT_H / 2 - STALL_D) + d)      // aisle edge         (|2.25|)
  const zB = g * ((LOT_H / 2) + d)                // row back           (|6.75|)
  const zO = g * ((LOT_H / 2 + ISL_ARM_W) - d)    // back outer         (|8.75|)
  return [
    [-XO, zF], [-XO, zO], [XO, zO], [XO, zF],     // outer: arm tip → back → arm tip
    [XI, zF], [XI, zB], [-XI, zB], [-XI, zF],     // notch: in, across the back, out
  ]
}

// Two independent landscaped islands, one wrapping each row. Each is a U-shaped
// grass median enclosed by its own continuous raised curb (an extruded U-ring +
// an inset grass fill that sits just below the rim). The arms wrap the grass
// around the end slots; the U opens to the aisle so the driveway stays clear.
function IslasCesped() {
  const islas = useMemo(() => {
    const innerR = Math.max(ISL_CORNER - ISL_CURB_W, 0.12)
    const build = (g) => {
      // Curb = U-ring: outer U outline with the inset U as a hole.
      const curbShape = roundedPolygonShape(islaUPoints(g, 0), ISL_CORNER)
      curbShape.holes.push(roundedPolygonShape(islaUPoints(g, ISL_CURB_W), innerR))
      const curb = new THREE.ExtrudeGeometry(curbShape, { depth: ISL_CURB_H, bevelEnabled: false })
      // Grass = solid U filling that hole, top just below the rim.
      const grassShape = roundedPolygonShape(islaUPoints(g, ISL_CURB_W), innerR)
      const grass = new THREE.ExtrudeGeometry(grassShape, { depth: ISL_CURB_H - 0.025, bevelEnabled: false })
      return { curb, grass }
    }
    return [build(-1), build(1)]
  }, [])

  return (
    <>
      {islas.map(({ curb, grass }, i) => (
        <group key={i}>
          {/* Continuous perimeter curb — one extruded U-ring */}
          <mesh geometry={curb} rotation-x={-Math.PI / 2} castShadow receiveShadow>
            <meshStandardMaterial color="#b0aca4" roughness={0.9} metalness={0.0} />
          </mesh>
          {/* Grass fill, recessed 2.5 cm so the curb reads as a raised rim */}
          <mesh geometry={grass} rotation-x={-Math.PI / 2} receiveShadow>
            <meshStandardMaterial color="#46793f" roughness={0.97} />
          </mesh>
        </group>
      ))}
    </>
  )
}

// Two concrete islands at the lamp gap — one per row, aisle left open between
function IslaFarol() {
  return (
    <>
      {[ISLAND_N_Z, ISLAND_S_Z].map((z) => (
        <mesh key={z} position={[LAMP_X, ISLAND_H / 2, z]} receiveShadow castShadow>
          <boxGeometry args={[LAMP_GAP, ISLAND_H, ISLAND_LEN]} />
          <meshStandardMaterial color="#a9a49d" roughness={0.94} metalness={0.0} />
        </mesh>
      ))}
    </>
  )
}

function MarcasCarril() {
  return (
    <>
      {[AISLE_N, AISLE_S].map((z) => (
        <mesh key={z} rotation-x={-Math.PI / 2} position={[0, 0.013, z]}>
          <planeGeometry args={[LOT_W - 0.5, 0.07]} />
          <meshStandardMaterial color="#d2cec4" roughness={0.88} transparent opacity={0.45} />
        </mesh>
      ))}
    </>
  )
}

// ---------------------------------------------------------------------------
// Lamp post — on the SOUTH island, arm reaching −Z over the aisle (the street)
// ---------------------------------------------------------------------------
function FarolLampara() {
  return (
    <group position={[LAMP_X, ISLAND_H, POLE_Z]}>
      {/* Compact concrete base pad */}
      <mesh position={[0, POLE_BASE_H / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[0.48, POLE_BASE_H, 0.48]} />
        <meshStandardMaterial color="#b2aea8" roughness={0.92} metalness={0.0} />
      </mesh>

      {/* Tapered collar */}
      <mesh position={[0, POLE_BASE_H + COLLAR_H / 2, 0]} castShadow>
        <cylinderGeometry args={[0.055, 0.095, COLLAR_H, 8]} />
        <meshStandardMaterial color="#9898a2" roughness={0.83} metalness={0.20} />
      </mesh>

      {/* Thin vertical mast */}
      <mesh position={[0, POLE_BASE_H + COLLAR_H + SHAFT_H / 2, 0]} castShadow>
        <boxGeometry args={[0.065, SHAFT_H, 0.065]} />
        <meshStandardMaterial color="#90909a" roughness={0.82} metalness={0.26} />
      </mesh>

      {/* Horizontal arm — box along −Z, reaching out over the aisle */}
      <mesh position={[0, POLE_TOP_Y, -ARM_L / 2]} castShadow>
        <boxGeometry args={[0.048, 0.048, ARM_L]} />
        <meshStandardMaterial color="#90909a" roughness={0.82} metalness={0.26} />
      </mesh>

      {/* Slim lamp housing at arm tip, over the aisle */}
      <mesh position={[0, POLE_TOP_Y - 0.038, -ARM_L]} castShadow>
        <boxGeometry args={[0.34, 0.08, 0.20]} />
        <meshStandardMaterial
          color="#b8b840"
          emissive="#fff8b0"
          emissiveIntensity={0.45}
          roughness={0.60}
          metalness={0.08}
        />
      </mesh>

      {/* Light aimed down onto the street (aisle centre) */}
      <pointLight
        position={[0, POLE_TOP_Y - 0.15, -ARM_L]}
        intensity={0.32}
        distance={22}
        color="#fff8d0"
        castShadow={false}
      />
    </group>
  )
}

// ---------------------------------------------------------------------------
// Vehicle model
// ---------------------------------------------------------------------------
function Vehiculo({ espacioId, rowZTL }) {
  const color = PALETA[Math.abs(hashCode(espacioId)) % PALETA.length]
  const rot = rowZTL < LOT_H / 2 ? 0 : Math.PI
  return (
    <group rotation-y={rot}>
      <mesh position={[0, 0.36, 0]} castShadow>
        <boxGeometry args={[1.82, 0.64, 4.1]} />
        <meshStandardMaterial color={color} metalness={0.28} roughness={0.60} />
      </mesh>
      <mesh position={[0, 0.85, -0.25]} castShadow>
        <boxGeometry args={[1.54, 0.48, 2.18]} />
        <meshStandardMaterial color={color} metalness={0.28} roughness={0.60} />
      </mesh>
      <mesh position={[0, 0.80, 0.86]} rotation-x={-0.30}>
        <boxGeometry args={[1.46, 0.44, 0.05]} />
        <meshStandardMaterial color="#7ec8e3" transparent opacity={0.48} metalness={0.08} roughness={0.04} />
      </mesh>
      <mesh position={[0, 0.80, -1.40]} rotation-x={0.30}>
        <boxGeometry args={[1.46, 0.40, 0.05]} />
        <meshStandardMaterial color="#7ec8e3" transparent opacity={0.38} metalness={0.08} roughness={0.04} />
      </mesh>
      {[[-0.92, -1.35], [0.92, -1.35], [-0.92, 1.35], [0.92, 1.35]].map(([wx, wz], i) => (
        <mesh key={i} position={[wx, 0.25, wz]} rotation-z={Math.PI / 2} castShadow>
          <cylinderGeometry args={[0.26, 0.26, 0.17, 12]} />
          <meshStandardMaterial color="#111111" roughness={0.96} />
        </mesh>
      ))}
    </group>
  )
}

// ---------------------------------------------------------------------------
// Parking stall
// ---------------------------------------------------------------------------
function Plaza({ espacio }) {
  let color = '#2e7d32'
  if (espacio.ocupado)        color = '#c0392b'
  else if (espacio.reservado) color = '#e67e22'

  const cx = espacio.x + OX
  const cz = espacio.z + OZ

  const seed      = hashCode(espacio.id)
  const weatherOp = 0.40 + seededRand(seed) * 0.10
  const lineOp    = 0.55 + seededRand(seed + 3) * 0.25

  return (
    <group position={[cx, 0, cz]}>
      {/* Translucent status tint */}
      <mesh rotation-x={-Math.PI / 2} position={[0, 0.005, 0]} receiveShadow>
        <planeGeometry args={[STALL_W - 0.04, STALL_D]} />
        <meshStandardMaterial color={color} transparent opacity={weatherOp} roughness={0.93} />
      </mesh>
      {/* Left side line */}
      <mesh rotation-x={-Math.PI / 2} position={[-(STALL_W / 2), 0.010, 0]}>
        <planeGeometry args={[0.065, STALL_D]} />
        <meshStandardMaterial color="#d0ccc2" roughness={0.88} transparent opacity={lineOp} />
      </mesh>
      {/* Right side line */}
      <mesh rotation-x={-Math.PI / 2} position={[STALL_W / 2, 0.010, 0]}>
        <planeGeometry args={[0.065, STALL_D]} />
        <meshStandardMaterial color="#d0ccc2" roughness={0.88} transparent opacity={lineOp} />
      </mesh>
      {espacio.ocupado && <Vehiculo espacioId={espacio.id} rowZTL={espacio.z} />}
    </group>
  )
}

// ---------------------------------------------------------------------------
// Route animation components
// ---------------------------------------------------------------------------
// Build visible Box-based route segments — more reliable than Line at all camera angles.
function SegmentoRuta({ p0, p1 }) {
  const cx = (p0[0] + p1[0]) / 2
  const cz = (p0[2] + p1[2]) / 2
  const dx = p1[0] - p0[0]
  const dz = p1[2] - p0[2]
  const len = Math.sqrt(dx * dx + dz * dz)
  const angle = -Math.atan2(dz, dx)
  if (len < 0.01) return null
  return (
    <mesh position={[cx, 0.9, cz]} rotation-y={angle}>
      <boxGeometry args={[len, 0.5, 0.75]} />
      <meshStandardMaterial color="#f97316" emissive="#f97316" emissiveIntensity={1.8} />
    </mesh>
  )
}

function RutaAnimada({ ruta }) {
  const dotRef = useRef()
  const elapsed = useRef(0)

  const puntos = useMemo(() => ruta.map((p) => [p.x, 1.0, p.z]), [ruta])

  const segLengths = useMemo(() => puntos.slice(1).map((p, i) => {
    const dx = p[0] - puntos[i][0]
    const dz = p[2] - puntos[i][2]
    return Math.sqrt(dx * dx + dz * dz)
  }), [puntos])

  const totalLen = useMemo(() => segLengths.reduce((a, b) => a + b, 0) || 1, [segLengths])

  useFrame((_, delta) => {
    elapsed.current = (elapsed.current + delta * 0.35) % 1
    let dist = elapsed.current * totalLen
    let idx = 0
    while (idx < segLengths.length - 1 && dist > segLengths[idx]) {
      dist -= segLengths[idx]
      idx++
    }
    const seg = segLengths[idx] || 1
    const alpha = Math.min(dist / seg, 1)
    const p0 = puntos[idx]
    const p1 = puntos[idx + 1] ?? p0
    if (dotRef.current) {
      dotRef.current.position.set(
        p0[0] + (p1[0] - p0[0]) * alpha,
        1.5,
        p0[2] + (p1[2] - p0[2]) * alpha,
      )
    }
  })

  if (puntos.length < 2) return null

  return (
    <>
      {puntos.slice(1).map((p, i) => (
        <SegmentoRuta key={i} p0={puntos[i]} p1={p} />
      ))}
      <mesh ref={dotRef} position={[puntos[0][0], 1.5, puntos[0][2]]}>
        <sphereGeometry args={[0.9, 16, 16]} />
        <meshStandardMaterial color="#f97316" emissive="#f97316" emissiveIntensity={2.5} />
      </mesh>
    </>
  )
}

function DestinoMarcador({ x, z }) {
  const ringRef = useRef()
  const pillarRef = useRef()
  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    if (ringRef.current) {
      const s = 1 + 0.2 * Math.sin(t * 3.0)
      ringRef.current.scale.setScalar(s)
    }
    if (pillarRef.current) {
      pillarRef.current.material.emissiveIntensity = 0.7 + 0.3 * Math.sin(t * 3.0)
    }
  })
  return (
    <group position={[x, 0, z]}>
      {/* Ground ring */}
      <mesh ref={ringRef} rotation-x={-Math.PI / 2} position={[0, 0.05, 0]}>
        <ringGeometry args={[0.9, 1.5, 32]} />
        <meshStandardMaterial color="#2563eb" emissive="#2563eb" emissiveIntensity={1.2} transparent opacity={0.95} />
      </mesh>
      {/* Vertical glowing pillar above the space */}
      <mesh ref={pillarRef} position={[0, 3.5, 0]}>
        <cylinderGeometry args={[0.28, 0.28, 6.0, 8]} />
        <meshStandardMaterial color="#2563eb" emissive="#2563eb" emissiveIntensity={1.5} transparent opacity={0.7} />
      </mesh>
    </group>
  )
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------
export function Parqueadero3D({ espacios: espaciosBackend = [], ruta = [], destino = null, animarRuta = false }) {
  const espacios = useMemo(() => {
    const mapa = new Map(espaciosBackend.map((e) => [e.id, e]))
    return ESPACIOS_ESTATICOS.map((e) => ({
      ...e,
      ocupado:   mapa.get(e.id)?.ocupado   ?? false,
      reservado: mapa.get(e.id)?.reservado ?? false,
    }))
  }, [espaciosBackend])

  return (
    <section className="scene-panel" aria-label="Vista 3D del parqueadero">
      <div className="scene-leyenda">
        <span className="leyenda-item leyenda-item--libre">Libre</span>
        <span className="leyenda-item leyenda-item--reservado">Reservado</span>
        <span className="leyenda-item leyenda-item--ocupado">Ocupado</span>
      </div>

      <Canvas
        shadows
        camera={{ position: [0, 30, 22], fov: animarRuta ? 58 : 52 }}
        gl={{ antialias: true }}
      >
        <color attach="background" args={['#b4cce0']} />

        <Sky sunPosition={[80, 22, 60]} turbidity={4} rayleigh={0.32} mieCoefficient={0.004} />

        <hemisphereLight intensity={0.40} color="#d8eaf8" groundColor="#2d3a28" />
        <directionalLight
          castShadow
          intensity={1.55}
          position={[28, 38, 18]}
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          shadow-camera-left={-48}
          shadow-camera-right={48}
          shadow-camera-top={14}
          shadow-camera-bottom={-14}
          shadow-bias={-0.0004}
          shadow-radius={1.5}
        />
        <directionalLight intensity={0.22} position={[-18, 12, -8]} />
        <Environment preset="park" />

        <Entorno />
        <Piso />
        <IslasCesped />
        <IslaFarol />
        <MarcasCarril />
        <FarolLampara />

        {espacios.map((e) => (
          <Plaza key={e.id} espacio={e} />
        ))}

        {animarRuta && ruta.length >= 2 && <RutaAnimada ruta={ruta} />}
        {animarRuta && destino && <DestinoMarcador x={destino.x} z={destino.z} />}

        <MapControls
          makeDefault
          minDistance={8}
          maxDistance={120}
          maxPolarAngle={Math.PI / 2 - 0.02}
          minPolarAngle={0.08}
          screenSpacePanning={false}
        />
      </Canvas>
    </section>
  )
}
