import { useState } from 'react'
import { Canvas } from '@react-three/fiber'
import DepthScene from './components/DepthScene'
import './App.css'

function App() {
  const [cameraType, setCameraType] = useState('perspective')

  return (
    <div className="app-container">
      <div className="info-panel">
        <h1>Espacios Proyectivos</h1>
        <p>Observa cómo cambia la percepción de profundidad con cada tipo de cámara.</p>
        <p><strong>Cámara Perspectiva:</strong> Los objetos lejanos se ven más pequeños (como nuestros ojos).</p>
        <p><strong>Cámara Ortográfica:</strong> Todos los objetos mantienen su tamaño sin importar la distancia.</p>
      </div>

      <div className="depth-info">
        <h3>Objetos en la Escena</h3>
        <ul>
          <li><span className="object-label">Cubo Rojo:</span> Profundidad: 0</li>
          <li><span className="object-label">Esfera Azul:</span> Profundidad: -5</li>
          <li><span className="object-label">Cono Verde:</span> Profundidad: -10</li>
        </ul>
      </div>

      <Canvas>
        <DepthScene cameraType={cameraType} />
      </Canvas>

      <div className="camera-controls">
        <button
          className={`camera-button ${cameraType === 'perspective' ? 'active' : ''}`}
          onClick={() => setCameraType('perspective')}
        >
          Cámara Perspectiva
        </button>
        <button
          className={`camera-button ${cameraType === 'orthographic' ? 'active' : ''}`}
          onClick={() => setCameraType('orthographic')}
        >
          Cámara Ortográfica
        </button>
      </div>
    </div>
  )
}

export default App
