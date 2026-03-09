import { useMemo, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { useGLTF, OrbitControls, Stars } from '@react-three/drei'
import { useControls } from 'leva'
import './App.css'

const MODEL_FILES = {
  sun: '/models/ps1_style_low_poly_sun.glb',
  earth: '/models/low_poly_planet_earth.glb',
  saturn: '/models/saturn_planet.glb',
  moon: '/models/low_poly_moon.glb',
}

function RotatingBody({ source, scale, spinRate = 0, initialRotation = [0, 0, 0] }) {
  const meshGroup = useRef()
  const { scene } = useGLTF(source)
  const clonedScene = useMemo(() => scene.clone(), [scene])

  useFrame((_, elapsed) => {
    if (!meshGroup.current || spinRate === 0) return
    meshGroup.current.rotation.y += elapsed * spinRate
  })

  return (
    <group ref={meshGroup} rotation={initialRotation}>
      <primitive object={clonedScene} scale={scale} />
    </group>
  )
}

function OrbitNode({
  orbitSpeed,
  radius,
  startAngle = 0,
  children,
}) {
  const orbitRoot = useRef()
  const phase = useRef(startAngle)

  useFrame((_, delta) => {
    phase.current += delta * orbitSpeed
    if (!orbitRoot.current) return
    orbitRoot.current.position.x = Math.cos(phase.current) * radius
    orbitRoot.current.position.z = Math.sin(phase.current) * radius
  })

  return <group ref={orbitRoot}>{children}</group>
}

function HierarchicalScene() {
  const {
    rotX,
    rotY,
    rotZ,
    trX,
    trY,
    trZ,
  } = useControls('🌞 Nodo raíz', {
    rotX: { value: 0, min: -Math.PI, max: Math.PI, step: 0.01, label: 'Rotación X' },
    rotY: { value: 0, min: -Math.PI, max: Math.PI, step: 0.01, label: 'Rotación Y' },
    rotZ: { value: 0, min: -Math.PI, max: Math.PI, step: 0.01, label: 'Rotación Z' },
    trX: { value: 0, min: -20, max: 20, step: 0.1, label: 'Traslación X' },
    trY: { value: 0, min: -20, max: 20, step: 0.1, label: 'Traslación Y' },
    trZ: { value: 0, min: -20, max: 20, step: 0.1, label: 'Traslación Z' },
  })

  const {
    sun,
    earth,
    saturn,
    moon,
  } = useControls('📐 Escalas', {
    sun: { value: 3, min: 0.5, max: 12, step: 0.1, label: 'Sol' },
    earth: { value: 80, min: 0.2, max: 200, step: 0.1, label: 'Tierra' },
    saturn: { value: 2.5, min: 0.2, max: 10, step: 0.1, label: 'Saturno' },
    moon: { value: 0.5, min: 0.1, max: 4, step: 0.05, label: 'Luna' },
  })

  const {
    earthOrbit,
    saturnOrbit,
    moonOrbit,
  } = useControls('🪐 Velocidad orbital', {
    earthOrbit: { value: 0.35, min: 0, max: 3, step: 0.01, label: 'Tierra' },
    saturnOrbit: { value: 0.18, min: 0, max: 3, step: 0.01, label: 'Saturno' },
    moonOrbit: { value: 1.2, min: 0, max: 5, step: 0.01, label: 'Luna' },
  })

  return (
    <group rotation={[rotX, rotY, rotZ]} position={[trX, trY, trZ]}>
      <pointLight intensity={4.8} distance={820} color="#ffe9c0" />

      <RotatingBody source={MODEL_FILES.sun} scale={sun} spinRate={0.25} />

      <OrbitNode orbitSpeed={earthOrbit} radius={sun * 10 + 40} startAngle={Math.PI * 0.3}>
        <RotatingBody source={MODEL_FILES.earth} scale={earth} spinRate={0.5} />

        <OrbitNode orbitSpeed={moonOrbit} radius={12}>
          <RotatingBody source={MODEL_FILES.moon} scale={moon} />
        </OrbitNode>
      </OrbitNode>

      <OrbitNode orbitSpeed={saturnOrbit} radius={sun * 10 + 140} startAngle={Math.PI}>
        <RotatingBody source={MODEL_FILES.saturn} scale={saturn} spinRate={0.3} />
      </OrbitNode>
    </group>
  )
}

function InterfacePanel() {
  return (
    <div className="hud-panel">
      <h1>Jerarquías de Transformación</h1>
      <p>Sol (nodo raíz) · Tierra/Saturno (nivel 2) · Luna (nivel 3)</p>
      <span>Usa el mouse para orbitar y Leva para ajustar órbitas, posición y escala.</span>
    </div>
  )
}

export default function App() {
  return (
    <main className="scene-shell">
      <Canvas camera={{ position: [0, 80, 180], fov: 60 }} gl={{ antialias: true }}>
        <ambientLight intensity={1.7} color="#a4b9ff" />
        <hemisphereLight skyColor="#7f8dff" groundColor="#2e154f" intensity={1.8} />

        <Stars
          radius={240}
          depth={100}
          count={9000}
          factor={7}
          saturation={0.9}
          fade
          speed={0.35}
        />

        <HierarchicalScene />
        <OrbitControls makeDefault />
      </Canvas>

      <InterfacePanel />
    </main>
  )
}

useGLTF.preload(MODEL_FILES.sun)
useGLTF.preload(MODEL_FILES.earth)
useGLTF.preload(MODEL_FILES.saturn)
useGLTF.preload(MODEL_FILES.moon)
