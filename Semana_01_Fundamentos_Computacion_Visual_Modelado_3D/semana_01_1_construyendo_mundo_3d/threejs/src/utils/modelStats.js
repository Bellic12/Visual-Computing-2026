export function calculateModelStats(rootObject) {
  const stats = {
    vertices: 0,
    faces: 0,
    meshes: 0,
  }

  rootObject.traverse((node) => {
    if (!node.isMesh || !node.geometry) {
      return
    }

    const { geometry } = node
    const positions = geometry.getAttribute('position')

    if (!positions) {
      return
    }

    stats.meshes += 1
    stats.vertices += positions.count

    const indexCount = geometry.getIndex()?.count
    stats.faces += indexCount ? indexCount / 3 : positions.count / 3
  })

  return {
    vertices: Math.trunc(stats.vertices),
    faces: Math.trunc(stats.faces),
    meshes: stats.meshes,
  }
}