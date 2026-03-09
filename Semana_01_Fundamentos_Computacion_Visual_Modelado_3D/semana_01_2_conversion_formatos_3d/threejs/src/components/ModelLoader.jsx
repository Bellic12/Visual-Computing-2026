import { useEffect, useMemo } from 'react'
import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import { clone } from 'three/examples/jsm/utils/SkeletonUtils.js'
import * as THREE from 'three'
import { computeModelStats, normalizeObject3D } from '../utils/modelUtils'

const MODEL_PATHS = {
  OBJ: '/low_poly_e30_rally_converted.obj',
  STL: '/scene_converted.stl',
  GLTF: '/Humvee_converted.gltf',
}

function prepareObjModel(objRoot) {
  const model = objRoot.clone(true)
  model.rotation.x = -Math.PI / 2
  return normalizeObject3D(model)
}

function prepareStlModel(stlGeometry) {
  const geometry = stlGeometry.clone()
  geometry.computeVertexNormals()

  const material = new THREE.MeshStandardMaterial({
    color: '#b0bccd',
    roughness: 0.45,
    metalness: 0.15,
  })

  const mesh = new THREE.Mesh(geometry, material)
  mesh.rotation.x = -Math.PI / 2
  return normalizeObject3D(mesh)
}

function prepareGltfModel(gltfScene) {
  const model = clone(gltfScene)
  return normalizeObject3D(model)
}

export default function ModelLoader({ activeFormat, onModelInfoChange }) {
  const objRoot = useLoader(OBJLoader, MODEL_PATHS.OBJ)
  const stlGeometry = useLoader(STLLoader, MODEL_PATHS.STL)
  const gltf = useLoader(GLTFLoader, MODEL_PATHS.GLTF)

  const models = useMemo(() => {
    const objModel = prepareObjModel(objRoot)
    const stlModel = prepareStlModel(stlGeometry)
    const gltfModel = prepareGltfModel(gltf.scene)

    return {
      OBJ: { object: objModel, stats: computeModelStats(objModel, 'OBJ') },
      STL: { object: stlModel, stats: computeModelStats(stlModel, 'STL') },
      GLTF: { object: gltfModel, stats: computeModelStats(gltfModel, 'GLTF') },
    }
  }, [gltf.scene, objRoot, stlGeometry])

  useEffect(() => {
    if (!models[activeFormat]) {
      return
    }

    onModelInfoChange(models[activeFormat].stats)
  }, [activeFormat, models, onModelInfoChange])

  return <primitive object={models[activeFormat].object} />
}
