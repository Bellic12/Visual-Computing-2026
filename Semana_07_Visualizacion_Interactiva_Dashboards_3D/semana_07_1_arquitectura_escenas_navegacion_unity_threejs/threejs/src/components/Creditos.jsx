import { Canvas, useFrame } from '@react-three/fiber'
import { Stars } from '@react-three/drei'
import { useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import './Creditos.css'

function CreditScene() {
  const meshRef = useRef(null)

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += delta * 0.2
      meshRef.current.rotation.y += delta * 0.25
    }
  })

  return (
    <>
      <ambientLight intensity={0.6} />
      <pointLight position={[5, 6, 5]} intensity={1.2} />
      <mesh ref={meshRef}>
        <icosahedronGeometry args={[2.2, 2]} />
        <meshStandardMaterial color="#22d3ee" wireframe={true} />
      </mesh>
      <Stars radius={60} depth={50} count={700} factor={4} fade speed={1} />
    </>
  )
}

export default function Creditos() {
  const navigate = useNavigate()

  return (
    <div className="scene-root">
      <Canvas className="scene-canvas" camera={{ position: [0, 3, 9], fov: 50 }}>
        <CreditScene />
      </Canvas>

      <div className="credits-overlay">
        <div className="credits-card">
          <h1>Creditos</h1>
          <p>
            Proyecto desarrollado para el Taller 62: Arquitectura de juego, escenas y navegacion en Three.js.
          </p>
          <div className="credits-grid">
            <div>
              <span>Estudiantes</span>
              <ul className="credits-list">
                <li>Juan David Buitrago Salazar</li>
                <li>Juan David Cardenas Galvis</li>
                <li>Nicolas Rodriguez Piraban</li>
                <li>Camilo Andres Medina Sanchez</li>
                <li>Juan Felipe Fajardo Garzon</li>
              </ul>
            </div>
            <div>
              <span>Fecha</span>
              <strong>25-04-2026</strong>
            </div>
            <div>
              <span>Tecnologias</span>
              <strong>React, Three.js, React Three Fiber</strong>
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            Volver al menu
          </button>
        </div>
      </div>
    </div>
  )
}
