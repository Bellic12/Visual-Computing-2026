import { useMemo, useState } from 'react'
import { CameraLabScene } from './components/CameraLabScene'
import { ControlPanel } from './components/ControlPanel'
import { ProjectionOverlay } from './components/ProjectionOverlay'
import { computeProjectionData } from './components/projectionMath'

const INITIAL_CAMERA = {
  fov: 58,
  aspect: 16 / 9,
  near: 0.5,
  far: 40,
  x: 2.4,
  y: 2.1,
  z: 8.4,
  yaw: -16,
  pitch: -11
}

const INITIAL_DISTORTION = {
  enabled: true,
  k1: 0.65,
  k2: -0.28,
  applyTo3d: true
}

export default function App() {
  const [cameraState, setCameraState] = useState(INITIAL_CAMERA)
  const [distortionState, setDistortionState] = useState(INITIAL_DISTORTION)
  const [viewMode, setViewMode] = useState('observer')

  const setCameraValue = (key, value) => {
    setCameraState((previous) => {
      const next = { ...previous, [key]: value }
      const minGap = 0.1

      if (key === 'near' && next.near >= next.far - minGap) {
        next.far = Number((next.near + minGap).toFixed(2))
      }

      if (key === 'far' && next.far <= next.near + minGap) {
        next.near = Math.max(0.1, Number((next.far - minGap).toFixed(2)))
      }

      next.near = Math.max(0.1, Number(next.near.toFixed(2)))
      next.far = Math.max(next.near + minGap, Number(next.far.toFixed(2)))

      return next
    })
  }

  const setDistortionValue = (key, value) => {
    setDistortionState((previous) => ({
      ...previous,
      [key]: value
    }))
  }

  const projectionData = useMemo(
    () => computeProjectionData(cameraState, distortionState),
    [cameraState, distortionState]
  )

  return (
    <div className="app-shell">
      <ControlPanel
        cameraState={cameraState}
        setCameraValue={setCameraValue}
        distortionState={distortionState}
        setDistortionValue={setDistortionValue}
        projectionData={projectionData}
        viewMode={viewMode}
        setViewMode={setViewMode}
      />

      <main className="workspace">
        <CameraLabScene
          cameraState={cameraState}
          viewMode={viewMode}
          distortionState={distortionState}
        />
        <ProjectionOverlay projectionData={projectionData} distortionState={distortionState} />
      </main>
    </div>
  )
}
