import { useMemo } from 'react'

function createMeshDescriptors(loadedModel) {
  const descriptors = []

  loadedModel.updateWorldMatrix(true, true)

  loadedModel.traverse((node) => {
    if (!node.isMesh || !node.geometry) {
      return
    }

    const firstMaterial = Array.isArray(node.material) ? node.material[0] : node.material

    descriptors.push({
      id: `${node.uuid}-${descriptors.length}`,
      geometry: node.geometry,
      matrix: node.matrixWorld.clone(),
      color: firstMaterial?.color?.getHex() ?? 0x385d7a,
    })
  })

  return descriptors
}

function BaseContextMesh({ descriptor }) {
  return (
    <mesh
      geometry={descriptor.geometry}
      matrix={descriptor.matrix}
      matrixAutoUpdate={false}
      frustumCulled={false}
      renderOrder={0}
    >
      <meshStandardMaterial
        color={descriptor.color}
        transparent
        opacity={0.2}
        depthWrite={false}
        metalness={0.05}
        roughness={0.9}
      />
    </mesh>
  )
}

function FacesOrEdgesMesh({ descriptor, wireframe }) {
  return (
    <mesh
      geometry={descriptor.geometry}
      matrix={descriptor.matrix}
      matrixAutoUpdate={false}
      frustumCulled={false}
    >
      <meshStandardMaterial color={descriptor.color} wireframe={wireframe} metalness={0.1} roughness={0.75} />
    </mesh>
  )
}

function VerticesMesh({ descriptor }) {
  return (
    <points
      geometry={descriptor.geometry}
      matrix={descriptor.matrix}
      matrixAutoUpdate={false}
      frustumCulled={false}
      renderOrder={2}
    >
      <pointsMaterial color={descriptor.color} size={0.05} sizeAttenuation />
    </points>
  )
}

function ModelVisual({ loadedModel, viewMode, showContextBase = true }) {
  const meshDescriptors = useMemo(() => createMeshDescriptors(loadedModel), [loadedModel])
  const shouldRenderBase = showContextBase && viewMode !== 'faces'

  return (
    <group>
      {meshDescriptors.map((descriptor) => {
        const contextBase = shouldRenderBase ? <BaseContextMesh key={`base-${descriptor.id}`} descriptor={descriptor} /> : null

        if (viewMode === 'vertices') {
          return (
            <group key={descriptor.id}>
              {contextBase}
              <VerticesMesh descriptor={descriptor} />
            </group>
          )
        }

        return (
          <group key={descriptor.id}>
            {contextBase}
            <FacesOrEdgesMesh
              descriptor={descriptor}
              wireframe={viewMode === 'edges'}
            />
          </group>
        )
      })}
    </group>
  )
}

export default ModelVisual