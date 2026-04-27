import { Canvas } from '@react-three/fiber'
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
  const color = espacio.ocupado ? '#c0392b' : '#2e7d32'

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

export function Parqueadero3D({ espacios, ruta, destino }) {
  return (
    <section className="scene-panel" aria-label="Vista 3D del parqueadero">
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
