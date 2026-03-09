import { useMemo } from 'react'
import { Canvas } from '@react-three/fiber'
import { calculateModelTransform } from '../../utils/modelTransform'
import ModelVisual from '../viewer/ModelVisual'

function ModelReferencePreview({ loadedModel, modelRotation }) {
  const { position, scale } = useMemo(
    () => calculateModelTransform(loadedModel, 1.8),
    [loadedModel],
  )

  return (
    <div className="preview-box" aria-label="Imagen de referencia del modelo">
      <Canvas camera={{ position: [2.8, 1.8, 2.8], fov: 45 }}>
        <color attach="background" args={['#eef3f8']} />
        <ambientLight intensity={0.75} />
        <directionalLight position={[3, 4, 2]} intensity={0.95} />

        {loadedModel && (
          <group position={position} scale={scale} rotation={modelRotation}>
            <ModelVisual loadedModel={loadedModel} viewMode="faces" showContextBase={false} />
          </group>
        )}
      </Canvas>
      {!loadedModel && <p className="preview-empty">Sin referencia</p>}
    </div>
  )
}

export default ModelReferencePreview