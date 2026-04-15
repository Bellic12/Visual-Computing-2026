export function disposeMaterial(material) {
  if (Array.isArray(material)) {
    material.forEach(disposeMaterial)
    return
  }

  material.dispose()
}

export function disposeScene(scene) {
  scene.traverse((object3D) => {
    if (object3D.geometry) {
      object3D.geometry.dispose()
    }

    if (object3D.material) {
      disposeMaterial(object3D.material)
    }
  })
}