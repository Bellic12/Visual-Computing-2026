import { Canvas } from '@react-three/fiber';
import { useState } from 'react';
import { CameraSystem } from './components/CameraSystem';
import { OverlayPanel } from './components/OverlayPanel';
import { SceneObjects } from './components/SceneObjects';
import {
  CAMERA_MODE,
  DEFAULT_ORTHOGRAPHIC,
  DEFAULT_PERSPECTIVE,
} from './constants/cameraConfig';

function App() {
  const [cameraMode, setCameraMode] = useState(CAMERA_MODE.PERSPECTIVE);
  const [fov, setFov] = useState(DEFAULT_PERSPECTIVE.fov);
  const [orthoSize, setOrthoSize] = useState(DEFAULT_ORTHOGRAPHIC.size);
  const [cameraTelemetry, setCameraTelemetry] = useState(null);
  const [projectionTelemetry, setProjectionTelemetry] = useState(null);
  const [resetToken, setResetToken] = useState(0);

  return (
    <main className="app-root">
      <Canvas dpr={[1, 2]} shadows>
        <color attach="background" args={['#edf2f4']} />
        <fog attach="fog" args={['#edf2f4', 20, 65]} />
        <CameraSystem
          mode={cameraMode}
          fov={fov}
          orthoSize={orthoSize}
          resetToken={resetToken}
          onTelemetry={setCameraTelemetry}
          onProjection={setProjectionTelemetry}
        />
        <SceneObjects />
      </Canvas>

      <div className="ui-layer">
        <OverlayPanel
          cameraMode={cameraMode}
          onCameraModeChange={setCameraMode}
          fov={fov}
          onFovChange={setFov}
          orthoSize={orthoSize}
          onOrthoSizeChange={setOrthoSize}
          onResetView={() => setResetToken((prev) => prev + 1)}
          cameraTelemetry={cameraTelemetry}
          projectionTelemetry={projectionTelemetry}
        />
      </div>
    </main>
  );
}

export default App;
