import { useState, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import PanoramaImage from './components/PanoramaImage.jsx'
import PanoramaVideo from './components/PanoramaVideo.jsx'
import Controls from './components/Controls.jsx'

export default function App() {
  const [mode, setMode] = useState('image')
  const videoRef = useRef(null)
  const [videoPlaying, setVideoPlaying] = useState(true)

  const toggleVideo = () => {
    const video = videoRef.current
    if (!video) return
    if (videoPlaying) {
      video.pause()
    } else {
      video.play()
    }
    setVideoPlaying(!videoPlaying)
  }

  return (
    <div className="app">
      <Canvas camera={{ position: [0, 0, 0.1], fov: 75 }}>
        {mode === 'image' ? <PanoramaImage /> : <PanoramaVideo videoRef={videoRef} />}
        <OrbitControls enableZoom={false} enablePan={false} rotateSpeed={0.5} />
      </Canvas>
      <Controls mode={mode} onModeChange={setMode} />
      {mode === 'video' && (
        <div className="video-controls">
          <button onClick={toggleVideo}>
            {videoPlaying ? 'Pausar' : 'Reanudar'}
          </button>
        </div>
      )}
    </div>
  )
}
