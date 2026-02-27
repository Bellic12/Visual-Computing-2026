import { useRef } from 'react'
import { OrbitControls, PerspectiveCamera, OrthographicCamera, Grid } from '@react-three/drei'
import * as THREE from 'three'

function DepthScene({ cameraType }) {
  const cubeRef = useRef()
  const sphereRef = useRef()
  const coneRef = useRef()

  return (
    <>
      <color attach="background" args={['#1a1a2e']} />
      
      {/* Luces */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <directionalLight position={[-10, -10, -5]} intensity={0.3} />
      <pointLight position={[0, 5, 0]} intensity={0.5} color="#61dafb" />

      {/* Cámara Perspectiva */}
      {cameraType === 'perspective' && (
        <PerspectiveCamera
          makeDefault
          position={[8, 6, 12]}
          fov={50}
        />
      )}

      {/* Cámara Ortográfica */}
      {cameraType === 'orthographic' && (
        <OrthographicCamera
          makeDefault
          position={[8, 6, 12]}
          zoom={50}
        />
      )}

      {/* OrbitControls */}
      <OrbitControls makeDefault />

      {/* Objeto 1: Cubo Rojo (Cerca - z=0) */}
      <mesh ref={cubeRef} position={[0, 1, 0]}>
        <boxGeometry args={[2, 2, 2]} />
        <meshStandardMaterial 
          color="#ff4444" 
          metalness={0.3}
          roughness={0.4}
        />
      </mesh>

      {/* Etiqueta para el cubo */}
      <mesh position={[0, 3, 0]}>
        <sphereGeometry args={[0.2, 32, 32]} />
        <meshBasicMaterial color="#ff4444" />
      </mesh>

      {/* Objeto 2: Esfera Azul (Media distancia - z=-5) */}
      <mesh ref={sphereRef} position={[0, 1, -5]}>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshStandardMaterial 
          color="#4444ff" 
          metalness={0.5}
          roughness={0.3}
        />
      </mesh>

      {/* Etiqueta para la esfera */}
      <mesh position={[0, 3, -5]}>
        <sphereGeometry args={[0.2, 32, 32]} />
        <meshBasicMaterial color="#4444ff" />
      </mesh>

      {/* Objeto 3: Cono Verde (Lejos - z=-10) */}
      <mesh ref={coneRef} position={[0, 1, -10]} rotation={[0, 0, 0]}>
        <coneGeometry args={[1.5, 3, 32]} />
        <meshStandardMaterial 
          color="#44ff44" 
          metalness={0.4}
          roughness={0.4}
        />
      </mesh>

      {/* Etiqueta para el cono */}
      <mesh position={[0, 3.5, -10]}>
        <sphereGeometry args={[0.2, 32, 32]} />
        <meshBasicMaterial color="#44ff44" />
      </mesh>

      {/* Líneas de referencia para mostrar la profundidad */}
      <group>
        {/* Línea desde el cubo hasta la esfera */}
        <Line
          points={[[0, 0, 0], [0, 0, -5]]}
          color="#888888"
          lineWidth={1}
          dashed
        />
        
        {/* Línea desde la esfera hasta el cono */}
        <Line
          points={[[0, 0, -5], [0, 0, -10]]}
          color="#888888"
          lineWidth={1}
          dashed
        />
      </group>

      {/* Grid */}
      <Grid 
        args={[20, 20]} 
        cellSize={1} 
        cellThickness={0.5} 
        cellColor="#6f6f6f" 
        sectionSize={5} 
        sectionThickness={1} 
        sectionColor="#9d4b4b" 
        fadeDistance={50} 
        fadeStrength={1} 
        followCamera={false}
        infiniteGrid={true}
      />
    </>
  )
}

// Componente auxiliar para dibujar líneas
function Line({ points, color, lineWidth, dashed }) {
  const ref = useRef()
  
  const geometry = new THREE.BufferGeometry().setFromPoints(
    points.map(p => new THREE.Vector3(...p))
  )
  
  return (
    <line ref={ref} geometry={geometry}>
      <lineBasicMaterial 
        color={color} 
        linewidth={lineWidth}
        linecap="round"
        linejoin="round"
        opacity={0.5}
        transparent
      />
    </line>
  )
}

export default DepthScene
