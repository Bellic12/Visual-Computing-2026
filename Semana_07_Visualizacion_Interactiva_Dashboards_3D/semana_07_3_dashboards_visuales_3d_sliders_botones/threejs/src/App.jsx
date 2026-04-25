import { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { Leva, button, folder, useControls } from 'leva'
import './App.css'

function ControlledShape({ scale, color, materialType, autoRotate }) {
  const meshRef = useRef(null)

  useFrame((_, delta) => {
    if (!meshRef.current || !autoRotate) {
      return
    }

    meshRef.current.rotation.y += delta * 1.1
    meshRef.current.rotation.x += delta * 0.45
  })

  return (
    <mesh ref={meshRef} scale={scale} position={[0, 0.2, 0]} castShadow receiveShadow>
      <torusKnotGeometry args={[0.9, 0.25, 180, 28]} />
      {materialType === 'standard' ? (
        <meshStandardMaterial color={color} roughness={0.25} metalness={0.55} />
      ) : (
        <meshPhongMaterial color={color} shininess={90} />
      )}
    </mesh>
  )
}

function App() {
  const [materialType, setMaterialType] = useState('standard')
  const [autoRotate, setAutoRotate] = useState(false)

  const { scale, color, lightIntensity, lightColor, lightX, lightY, lightZ } =
    useControls('Escena 3D', {
      scale: {
        label: 'Escala del objeto',
        value: 1,
        min: 0.5,
        max: 2.6,
        step: 0.05,
      },
      color: {
        label: 'Color del objeto',
        value: '#ef7d2a',
      },
      Luz: folder({
        lightIntensity: {
          label: 'Intensidad',
          value: 2.1,
          min: 0,
          max: 6,
          step: 0.1,
        },
        lightColor: {
          label: 'Color',
          value: '#d8fff2',
        },
        lightX: {
          label: 'Posicion X',
          value: 3,
          min: -8,
          max: 8,
          step: 0.1,
        },
        lightY: {
          label: 'Posicion Y',
          value: 5,
          min: -2,
          max: 10,
          step: 0.1,
        },
        lightZ: {
          label: 'Posicion Z',
          value: 4,
          min: -8,
          max: 8,
          step: 0.1,
        },
      }),
    })

  useControls('Acciones', {
    alternarMaterial: button(() => {
      setMaterialType((current) =>
        current === 'standard' ? 'phong' : 'standard',
      )
    }),
    alternarRotacion: button(() => {
      setAutoRotate((current) => !current)
    }),
  })

  return (
    <main className="dashboard">
      <header className="panel">
        <p className="eyebrow">Taller Semana 7</p>
        <h1>Dashboard Visual 3D</h1>
        <p className="description">
          Usa el panel lateral para cambiar escala, color y luz en tiempo real.
          Tambien puedes activar la rotacion y alternar materiales con botones.
        </p>
        <div className="status-row">
          <span>Material: {materialType}</span>
          <span>Rotacion: {autoRotate ? 'Activa' : 'Inactiva'}</span>
        </div>
      </header>

      <section className="scene-grid">
        <section className="viewport">
          <Canvas shadows camera={{ position: [0, 1.8, 5], fov: 48 }}>
            <color attach="background" args={['#07121d']} />
            <fog attach="fog" args={['#07121d', 8, 18]} />

            <ambientLight intensity={0.35} color="#cce7ff" />
            <directionalLight
              position={[lightX, lightY, lightZ]}
              intensity={lightIntensity}
              color={lightColor}
              castShadow
              shadow-mapSize-width={1024}
              shadow-mapSize-height={1024}
            />

            <mesh
              rotation={[-Math.PI / 2, 0, 0]}
              position={[0, -1.3, 0]}
              receiveShadow
            >
              <circleGeometry args={[6, 72]} />
              <meshStandardMaterial color="#0f2437" roughness={0.9} />
            </mesh>

            <ControlledShape
              scale={scale}
              color={color}
              materialType={materialType}
              autoRotate={autoRotate}
            />
            <OrbitControls enableDamping dampingFactor={0.07} />
          </Canvas>
        </section>

        <aside className="controls-wrap">
          <Leva
            titleBar={{ title: 'Controles' }}
            collapsed={false}
            fill
            flat
            oneLineLabels
          />
        </aside>
      </section>
    </main>
  )
}

export default App
