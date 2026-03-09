import { useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { calculateModelTransform } from '../../utils/modelTransform'
import ModelVisual from './ModelVisual'

function EmptyState() {
  return (
    <mesh>
      <sphereGeometry args={[0.35, 24, 24]} />
      <meshStandardMaterial color="#8ea2b7" wireframe />
    </mesh>
  )
}

function ModelCanvas({ loadedModel, viewMode, modelRotation }) {
  const { position, scale } = useMemo(() => calculateModelTransform(loadedModel, 3), [loadedModel])

  return (
    <div className="canvas-root">
      <Canvas camera={{ position: [4.5, 2.5, 4.5], fov: 50 }}>
        <color attach="background" args={['#f2f5f8']} />
        <ambientLight intensity={0.85} />
        <directionalLight position={[4, 6, 3]} intensity={1.1} />

        <group position={position} scale={scale} rotation={modelRotation}>
          {loadedModel ? <ModelVisual loadedModel={loadedModel} viewMode={viewMode} /> : <EmptyState />}
        </group>

        <OrbitControls makeDefault enableDamping />
      </Canvas>
    </div>
  )
}

export default ModelCanvas