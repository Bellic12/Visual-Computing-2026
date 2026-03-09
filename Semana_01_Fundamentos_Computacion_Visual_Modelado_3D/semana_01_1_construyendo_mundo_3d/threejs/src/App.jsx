import { useMemo, useState } from 'react'
import ModelCanvas from './components/viewer/ModelCanvas'
import ControlPanel from './components/ui/ControlPanel'
import { useModelLoader } from './hooks/useModelLoader'
import './App.css'

const ROTATION_STEP = Math.PI / 2

function getDefaultRotationByFormat(modelFormat) {
  if (modelFormat === 'stl') {
    return [-Math.PI / 2, 0, 0]
  }

  return [0, 0, 0]
}

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [viewMode, setViewMode] = useState('faces')
  const [rotationOffset, setRotationOffset] = useState([0, 0, 0])

  const {
    loadedModel,
    modelStats,
    loadingError,
    isLoading,
    modelFormat,
  } = useModelLoader(selectedFile)

  const baseRotation = useMemo(() => getDefaultRotationByFormat(modelFormat), [modelFormat])
  const modelRotation = useMemo(
    () => baseRotation.map((value, index) => value + rotationOffset[index]),
    [baseRotation, rotationOffset],
  )

  const handleFileSelected = (file) => {
    setSelectedFile(file)
    setRotationOffset([0, 0, 0])
  }

  const rotateModel = (axisIndex, direction) => {
    setRotationOffset((currentOffset) => {
      const updatedRotation = [...currentOffset]
      updatedRotation[axisIndex] += ROTATION_STEP * direction
      return updatedRotation
    })
  }

  const resetRotation = () => {
    setRotationOffset([0, 0, 0])
  }

  return (
    <main className="app-layout">
      <ControlPanel
        selectedFileName={selectedFile?.name ?? 'Sin archivo'}
        loadedModel={loadedModel}
        modelStats={modelStats}
        viewMode={viewMode}
        modelRotation={modelRotation}
        isLoading={isLoading}
        loadingError={loadingError}
        onModeChange={setViewMode}
        onRotateModel={rotateModel}
        onResetRotation={resetRotation}
        onFileSelected={handleFileSelected}
      />
      <section className="viewer-section" aria-label="Visor 3D">
        <ModelCanvas loadedModel={loadedModel} viewMode={viewMode} modelRotation={modelRotation} />
      </section>
    </main>
  )
}

export default App
