import { useEffect, useState } from 'react'
import { Mesh, MeshStandardMaterial } from 'three'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { calculateModelStats } from '../utils/modelStats'

const supportedExtensions = new Set(['obj', 'stl', 'gltf', 'glb'])

function getFileExtension(fileName) {
  const segments = fileName.split('.')
  return segments.length > 1 ? segments.pop().toLowerCase() : ''
}

function parseGltfFromBuffer(arrayBuffer) {
  const loader = new GLTFLoader()

  return new Promise((resolve, reject) => {
    loader.parse(
      arrayBuffer,
      '',
      (gltf) => resolve(gltf.scene || gltf.scenes?.[0]),
      (error) => reject(error),
    )
  })
}

async function parseModelFile(file) {
  const extension = getFileExtension(file.name)

  if (!supportedExtensions.has(extension)) {
    throw new Error('Formato no soportado. Usa .obj, .stl, .gltf o .glb')
  }

  if (extension === 'obj') {
    const fileContent = await file.text()
    return {
      model: new OBJLoader().parse(fileContent),
      modelFormat: extension,
    }
  }

  if (extension === 'stl') {
    const fileBuffer = await file.arrayBuffer()
    const geometry = new STLLoader().parse(fileBuffer)
    geometry.computeBoundingBox()
    geometry.center()
    geometry.computeVertexNormals()
    return {
      model: new Mesh(geometry, new MeshStandardMaterial({ color: '#385d7a' })),
      modelFormat: extension,
    }
  }

  const fileBuffer = await file.arrayBuffer()
  const scene = await parseGltfFromBuffer(fileBuffer)

  if (!scene) {
    throw new Error('No se pudo leer el contenido del archivo GLTF/GLB')
  }

  return {
    model: scene,
    modelFormat: extension,
  }
}

const emptyStats = {
  vertices: 0,
  faces: 0,
  meshes: 0,
}

export function useModelLoader(selectedFile) {
  const [loadedModel, setLoadedModel] = useState(null)
  const [modelFormat, setModelFormat] = useState('')
  const [modelStats, setModelStats] = useState(emptyStats)
  const [isLoading, setIsLoading] = useState(false)
  const [loadingError, setLoadingError] = useState('')

  useEffect(() => {
    let isActive = true

    if (!selectedFile) {
      setLoadedModel(null)
      setModelFormat('')
      setModelStats(emptyStats)
      setLoadingError('')
      setIsLoading(false)
      return undefined
    }

    async function loadModel() {
      setIsLoading(true)
      setLoadingError('')

      try {
        const { model, modelFormat: parsedFormat } = await parseModelFile(selectedFile)

        if (!isActive) {
          return
        }

        setLoadedModel(model)
        setModelFormat(parsedFormat)
        setModelStats(calculateModelStats(model))
      } catch (error) {
        if (!isActive) {
          return
        }

        setLoadedModel(null)
        setModelFormat('')
        setModelStats(emptyStats)
        setLoadingError(error instanceof Error ? error.message : 'No se pudo cargar el modelo')
      } finally {
        if (isActive) {
          setIsLoading(false)
        }
      }
    }

    loadModel()

    return () => {
      isActive = false
    }
  }, [selectedFile])

  return {
    loadedModel,
    modelFormat,
    modelStats,
    isLoading,
    loadingError,
  }
}