import * as THREE from 'three'

export const FORMAT_OPTIONS = ['OBJ', 'STL', 'GLTF']

function addGeometryOverlays(mesh) {
  if (mesh.userData.overlaysReady || !mesh.geometry) {
    return
  }

  const edgeGeometry = new THREE.EdgesGeometry(mesh.geometry)
  const edgeMaterial = new THREE.LineBasicMaterial({
    color: '#3d43ff',
    transparent: true,
    opacity: 0.6,
  })

  const edgeLines = new THREE.LineSegments(edgeGeometry, edgeMaterial)
  edgeLines.renderOrder = 1

  const vertexMaterial = new THREE.PointsMaterial({
    color: '#ff9a5f',
    size: 0.015,
    sizeAttenuation: true,
    transparent: true,
    opacity: 0.5,
    depthWrite: false,
  })

  const vertices = new THREE.Points(mesh.geometry, vertexMaterial)
  vertices.renderOrder = 2

  mesh.add(edgeLines)
  mesh.add(vertices)
  mesh.userData.overlaysReady = true
}

function ensureMeshShadows(object3d) {
  object3d.traverse((node) => {
    if (node.isMesh) {
      node.castShadow = true
      node.receiveShadow = true
      if (!node.material) {
        node.material = new THREE.MeshStandardMaterial({ color: '#bfc6d4', roughness: 0.55, metalness: 0.1 })
      }

      addGeometryOverlays(node)
    }
  })
}

export function normalizeObject3D(object3d, targetSize = 2.6) {
  const box = new THREE.Box3().setFromObject(object3d)
  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())
  const maxAxis = Math.max(size.x, size.y, size.z)

  if (maxAxis > 0) {
    const scale = targetSize / maxAxis
    object3d.scale.multiplyScalar(scale)
  }

  // Centra el modelo para comparar formatos en el mismo encuadre.
  object3d.position.sub(center.multiplyScalar(object3d.scale.x))
  ensureMeshShadows(object3d)
  return object3d
}

export function computeModelStats(object3d, format) {
  let vertices = 0
  let faces = 0

  object3d.traverse((node) => {
    if (!node.isMesh || !node.geometry) {
      return
    }

    const geometry = node.geometry
    const positionAttribute = geometry.getAttribute('position')

    if (positionAttribute) {
      vertices += positionAttribute.count
    }

    if (geometry.index) {
      faces += Math.floor(geometry.index.count / 3)
    } else if (positionAttribute) {
      faces += Math.floor(positionAttribute.count / 3)
    }
  })

  return {
    format,
    vertices,
    faces,
  }
}
