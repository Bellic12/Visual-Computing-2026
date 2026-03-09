import { useCallback, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Grid, Line, OrbitControls, Stars } from '@react-three/drei'
import './App.css'

const SCENE_THEME = {
  moverFill: '#f59e0b',
  moverEmission: '#7c2d12',
  accentLight: '#fb7185',
  pathTrack: '#fcd34d',
  floorThin: '#f97316',
  floorThick: '#f59e0b',
  backdrop: 'linear-gradient(150deg, #13091d, #25143a, #3f1d57)',
}

const PATH_SETTINGS = {
  orbitSize: 2.5,
  depthSwing: 1.2,
}

const SPIN_STEPS = {
  x: 0.012,
  y: 0.018,
  z: 0.008,
}

function AnimatedSolid({ onTelemetry }) {
  const solidRef = useRef(null)

  useFrame((state) => {
    const solid = solidRef.current
    if (!solid) return

    const t = state.clock.elapsedTime
    const movementX = Math.cos(t * 0.8) * PATH_SETTINGS.orbitSize
    const movementY = Math.sin(t * 0.8) * PATH_SETTINGS.orbitSize
    const movementZ = Math.sin(t * 1.2) * PATH_SETTINGS.depthSwing
    solid.position.set(movementX, movementY, movementZ)

    solid.rotation.x += SPIN_STEPS.x
    solid.rotation.y += SPIN_STEPS.y
    solid.rotation.z += SPIN_STEPS.z

    const smoothScale = 1 + 0.4 * Math.sin(t * 2)
    solid.scale.setScalar(smoothScale)

    onTelemetry({
      position: { x: movementX, y: movementY, z: movementZ },
      rotation: { x: solid.rotation.x, y: solid.rotation.y, z: solid.rotation.z },
      scale: smoothScale,
      time: t,
    })
  })

  return (
    <mesh ref={solidRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial
        color={SCENE_THEME.moverFill}
        metalness={0.3}
        roughness={0.4}
        emissive={SCENE_THEME.moverEmission}
        emissiveIntensity={0.2}
      />
    </mesh>
  )
}

function OrbitTrail() {
  const sampledPath = useMemo(() => {
    const loopDuration = Math.PI * 10
    const totalSamples = 260
    return Array.from({ length: totalSamples }, (_, sampleIndex) => {
      const ratio = sampleIndex / (totalSamples - 1)
      const localTime = ratio * loopDuration
      return [
        Math.cos(localTime * 0.8) * PATH_SETTINGS.orbitSize,
        Math.sin(localTime * 0.8) * PATH_SETTINGS.orbitSize,
        Math.sin(localTime * 1.2) * PATH_SETTINGS.depthSwing,
      ]
    })
  }, [])

  return (
    <Line
      points={sampledPath}
      color={SCENE_THEME.pathTrack}
      dashed
      dashSize={0.2}
      gapSize={0.15}
      opacity={0.85}
      transparent
    />
  )
}

function SceneRig({ onTelemetry }) {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 8, 5]} intensity={1.2} castShadow />
      <pointLight position={[-4, -2, -4]} intensity={0.6} color={SCENE_THEME.accentLight} />

      <OrbitTrail />
      <AnimatedSolid onTelemetry={onTelemetry} />

      <Grid
        args={[12, 12]}
        position={[0, -3.5, 0]}
        cellColor={SCENE_THEME.floorThin}
        sectionColor={SCENE_THEME.floorThick}
        fadeDistance={20}
      />
      <Stars radius={40} depth={30} count={1500} factor={3} fade />

      <OrbitControls enableDamping dampingFactor={0.08} />
    </>
  )
}

function readMetric(value) {
  return value.toFixed(2)
}

function HeadUpDisplay({ telemetry }) {
  return (
    <aside className="hud-panel">
      <h1>Transformaciones 3D</h1>
      <ul>
        <li><span className="signal signal-motion" /> Traslación — trayectoria circular</li>
        <li><span className="signal signal-spin" /> Rotación — incremento por frame</li>
        <li><span className="signal signal-pulse" /> Escala — pulso con Math.sin</li>
      </ul>

      <div className="metrics">
        <p className="metrics-title">Estado del cubo</p>
        <p>Posición X: {readMetric(telemetry.position.x)}</p>
        <p>Posición Y: {readMetric(telemetry.position.y)}</p>
        <p>Posición Z: {readMetric(telemetry.position.z)}</p>
        <p>Escala: {readMetric(telemetry.scale)}</p>
        <p>Rotación X: {readMetric(telemetry.rotation.x)}</p>
        <p>Rotación Y: {readMetric(telemetry.rotation.y)}</p>
        <p>Rotación Z: {readMetric(telemetry.rotation.z)}</p>
        <p>Tiempo: {readMetric(telemetry.time)} s</p>
      </div>

      <p className="helper">🖱 Arrastra para orbitar · Scroll para zoom</p>
    </aside>
  )
}

function App() {
  const [telemetry, setTelemetry] = useState({
    position: { x: PATH_SETTINGS.orbitSize, y: 0, z: 0 },
    rotation: { x: 0, y: 0, z: 0 },
    scale: 1,
    time: 0,
  })

  const pushTelemetry = useCallback((snapshot) => {
    setTelemetry(snapshot)
  }, [])

  const cameraConfig = { position: [0, 0, 9], fov: 60 }

  return (
    <main className="viewport-shell">
      <HeadUpDisplay telemetry={telemetry} />
      <Canvas shadows camera={cameraConfig} style={{ background: SCENE_THEME.backdrop }}>
        <SceneRig onTelemetry={pushTelemetry} />
      </Canvas>
    </main>
  )
}

export default App
