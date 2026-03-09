import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { Suspense } from 'react'
import ModelLoader from './ModelLoader'

function SceneLights() {
  return (
    <>
      <ambientLight intensity={0.85} />
      <hemisphereLight args={['#d8e6ff', '#1f2430', 0.6]} />
      <directionalLight
        position={[5, 8, 5]}
        intensity={1.35}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      <directionalLight position={[-4, 5, -4]} intensity={0.65} />
      <pointLight position={[-5, 3, -5]} intensity={0.4} />
    </>
  )
}

function Ground() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.45, 0]} receiveShadow>
      <planeGeometry args={[20, 20]} />
      <shadowMaterial opacity={0.28} />
    </mesh>
  )
}

export default function Scene({ activeFormat, onModelInfoChange }) {
  return (
    <Canvas
      shadows
      camera={{ position: [4.8, 3.6, 6], fov: 48 }}
      gl={{ antialias: true }}
    >
      <color attach="background" args={['#1a1f29']} />
      <SceneLights />
      <Ground />
      <Suspense fallback={null}>
        <ModelLoader
          activeFormat={activeFormat}
          onModelInfoChange={onModelInfoChange}
        />
      </Suspense>
      <OrbitControls
        enableDamping
        dampingFactor={0.08}
        minDistance={1.5}
        maxDistance={16}
      />
    </Canvas>
  )
}
