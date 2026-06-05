import { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Environment, Line, OrbitControls, Text } from '@react-three/drei'

function Piso() {
  return (
    <mesh rotation-x={-Math.PI / 2} position={[0, -0.02, 0]} receiveShadow>
      <planeGeometry args={[36, 24]} />
      <meshStandardMaterial color="#ece7dd" />
    </mesh>
  )
}

function Plaza({ espacio }) {
  let color = '#2e7d32'
  if (espacio.ocupado) color = '#c0392b'
  else if (espacio.reservado) color = '#e67e22'

  return (
    <group position={[espacio.x, 0, espacio.z]}>
      <mesh rotation-x={-Math.PI / 2} receiveShadow>
        <planeGeometry args={[2.0, 4.1]} />
        <meshStandardMaterial color={color} roughness={0.7} />
      </mesh>

      {espacio.ocupado ? (
        <mesh position={[0, 0.65, 0]} castShadow>
          <boxGeometry args={[1.3, 1.05, 2.95]} />
          <meshStandardMaterial color="#38495a" metalness={0.15} roughness={0.4} />
        </mesh>
      ) : null}

      <Text
        position={[0, 0.08, -2.35]}
        rotation-x={-Math.PI / 2}
        fontSize={0.35}
        color="#111111"
        anchorX="center"
        anchorY="middle"
      >
        {espacio.id}
      </Text>
    </group>
  )
}

function RutaOptima({ ruta }) {
  if (!Array.isArray(ruta) || ruta.length < 2) {
    return null
  }

  const puntos = ruta.flatMap((punto) => [punto.x, 0.06, punto.z])

  return (
    <Line
      points={puntos}
      color="#1f6feb"
      lineWidth={3}
      transparent
      opacity={0.9}
    />
  )
}

function AnimacionRuta({ ruta }) {
  const ref = useRef()
  const progreso = useRef(0)

  useFrame((_, delta) => {
    if (!ruta || ruta.length < 2 || !ref.current) return
    progreso.current = (progreso.current + delta * 0.22) % 1

    const totalSegmentos = ruta.length - 1
    const avance = progreso.current * totalSegmentos
    const segmento = Math.floor(avance)
    const t = avance - segmento

    const desde = ruta[Math.min(segmento, ruta.length - 1)]
    const hasta = ruta[Math.min(segmento + 1, ruta.length - 1)]

    if (desde && hasta) {
      ref.current.position.x = desde.x + (hasta.x - desde.x) * t
      ref.current.position.z = desde.z + (hasta.z - desde.z) * t
    }
  })

  if (!ruta || ruta.length < 2) return null

  return (
    <mesh ref={ref} position={[ruta[0].x, 0.4, ruta[0].z]} castShadow>
      <sphereGeometry args={[0.28, 16, 16]} />
      <meshStandardMaterial color="#f39c12" emissive="#f39c12" emissiveIntensity={0.9} />
    </mesh>
  )
}

export function Parqueadero3D({ espacios, ruta, destino, animarRuta = false }) {
  return (
    <section className="scene-panel" aria-label="Vista 3D del parqueadero">
      <div className="scene-leyenda">
        <span className="leyenda-item leyenda-item--libre">Libre</span>
        <span className="leyenda-item leyenda-item--reservado">Reservado</span>
        <span className="leyenda-item leyenda-item--ocupado">Ocupado</span>
      </div>
      <Canvas shadows camera={{ position: [9, 13, 12], fov: 50 }}>
        <color attach="background" args={['#f6f2ea']} />
        <hemisphereLight intensity={0.5} color="#fff3d4" groundColor="#2b2b2b" />
        <directionalLight
          castShadow
          intensity={1.3}
          position={[8, 14, 7]}
          shadow-mapSize-width={1024}
          shadow-mapSize-height={1024}
        />
        <Piso />
        {espacios.map((espacio) => (
          <Plaza key={espacio.id} espacio={espacio} />
        ))}
        <RutaOptima ruta={ruta} />
        {animarRuta ? <AnimacionRuta ruta={ruta} /> : null}
        {destino ? (
          <mesh position={[destino.x, 0.12, destino.z]} castShadow>
            <sphereGeometry args={[0.22, 24, 24]} />
            <meshStandardMaterial color="#1f6feb" emissive="#1f6feb" emissiveIntensity={0.6} />
          </mesh>
        ) : null}
        <Environment preset="sunset" />
        <OrbitControls makeDefault minDistance={8} maxDistance={30} />
      </Canvas>
    </section>
  )
}
