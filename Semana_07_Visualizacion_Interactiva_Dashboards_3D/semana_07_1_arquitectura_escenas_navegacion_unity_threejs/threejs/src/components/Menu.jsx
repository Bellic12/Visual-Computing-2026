import { Canvas, useFrame } from '@react-three/fiber'
import { Stars } from '@react-three/drei'
import { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import './Menu.css'

function HeroScene() {
  const ringRef = useRef(null)
  const satelliteRef = useRef(null)

  useFrame((state, delta) => {
    if (ringRef.current) {
      ringRef.current.rotation.x += delta * 0.3
      ringRef.current.rotation.y += delta * 0.2
    }

    if (satelliteRef.current) {
      const t = state.clock.getElapsedTime()
      const r = 3.2
      satelliteRef.current.position.set(Math.cos(t) * r, 0.6, Math.sin(t) * r)
    }
  })

  return (
    <>
      <ambientLight intensity={0.6} />
      <pointLight position={[6, 8, 6]} intensity={1.2} />
      <pointLight position={[-6, -4, -6]} intensity={0.6} color="#ffb86b" />

      <mesh>
        <sphereGeometry args={[1.6, 32, 32]} />
        <meshStandardMaterial color="#1c2541" emissive="#1a2a52" emissiveIntensity={0.6} />
      </mesh>

      <mesh ref={ringRef}>
        <torusGeometry args={[3.8, 0.08, 24, 180]} />
        <meshStandardMaterial color="#22d3ee" emissive="#22d3ee" emissiveIntensity={0.5} />
      </mesh>

      <mesh ref={satelliteRef}>
        <sphereGeometry args={[0.22, 16, 16]} />
        <meshStandardMaterial color="#ffb86b" emissive="#ffb86b" emissiveIntensity={0.8} />
      </mesh>

      <Stars radius={60} depth={50} count={900} factor={4} fade speed={1} />
    </>
  )
}

export default function Menu() {
  const navigate = useNavigate()

  return (
    <div className="scene-root">
      <Canvas className="scene-canvas" camera={{ position: [0, 4, 10], fov: 50 }}>
        <HeroScene />
      </Canvas>

      <div className="menu-overlay">
        <div className="menu-card">
          <p className="menu-kicker">Taller 62</p>
          <h1 className="menu-title">Orbital Runner 3D</h1>
          <p className="menu-subtitle">
            Corre sobre orbitas luminiscentes, esquiva obstaculos y mantente en el carril correcto.
          </p>
          <div className="menu-actions">
            <button className="btn btn-primary" onClick={() => navigate('/juego')}>
              Iniciar juego
            </button>
            <button className="btn btn-ghost" onClick={() => navigate('/creditos')}>
              Creditos
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
