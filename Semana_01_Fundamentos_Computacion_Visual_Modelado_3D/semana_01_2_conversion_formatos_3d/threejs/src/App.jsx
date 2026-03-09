import { useState } from 'react'
import './App.css'
import Scene from './components/Scene'
import UIControls from './components/UIControls'

const DEFAULT_INFO = {
  format: 'OBJ',
  vertices: 0,
  faces: 0,
}

function App() {
  const [activeFormat, setActiveFormat] = useState('OBJ')
  const [modelInfo, setModelInfo] = useState(DEFAULT_INFO)

  return (
    <main className="app-layout">
      <header className="app-header">
        <h1>Comparador de Formatos 3D</h1>
        <p>Visualiza diferencias de geometría, materiales, texturas y suavizado entre OBJ, STL y GLTF.</p>
      </header>

      <section className="viewer-section">
        <div className="scene-wrapper">
          <Scene
            activeFormat={activeFormat}
            onModelInfoChange={setModelInfo}
          />
        </div>

        <UIControls
          activeFormat={activeFormat}
          onFormatChange={setActiveFormat}
          modelInfo={modelInfo}
        />
      </section>
    </main>
  )
}

export default App
