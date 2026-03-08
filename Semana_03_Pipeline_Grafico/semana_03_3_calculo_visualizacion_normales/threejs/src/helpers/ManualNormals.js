import * as THREE from 'three'

export function computeNormalsManually(geometry) {
  const position = geometry.attributes.position
  const normals = new Float32Array(position.count * 3)

  for (let i = 0; i < position.count; i += 3) {
    const a = new THREE.Vector3().fromBufferAttribute(position, i)
    const b = new THREE.Vector3().fromBufferAttribute(position, i + 1)
    const c = new THREE.Vector3().fromBufferAttribute(position, i + 2)

    const cb = new THREE.Vector3().subVectors(c, b)
    const ab = new THREE.Vector3().subVectors(a, b)
    const normal = new THREE.Vector3().crossVectors(cb, ab).normalize()

    for (let j = 0; j < 3; j++) {
      normals[(i + j) * 3 + 0] = normal.x
      normals[(i + j) * 3 + 1] = normal.y
      normals[(i + j) * 3 + 2] = normal.z
    }
  } 

  geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3))
}
