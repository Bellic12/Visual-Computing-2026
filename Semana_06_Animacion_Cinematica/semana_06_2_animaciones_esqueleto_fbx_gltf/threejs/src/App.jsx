import { Canvas } from '@react-three/fiber';
import { ContactShadows, Environment, OrbitControls } from '@react-three/drei';
import { Suspense, useCallback, useEffect, useRef, useState } from 'react';
import AnimatedCharacter from './components/AnimatedCharacter.jsx';
import DanceMarker from './components/DanceMarker.jsx';

export default function App() {
  const [clipNames, setClipNames] = useState([]);
  const [activeClip, setActiveClip] = useState(null);
  const [mode, setMode] = useState('dance');
  const [replaySignal, setReplaySignal] = useState(0);
  const [hasAnimation, setHasAnimation] = useState(false);
  const progressRef = useRef(0);

  const defaultClip = clipNames[0] ?? null;

  const handleClips = useCallback((names) => {
    setClipNames(names);
    setActiveClip((current) => current ?? names[0] ?? null);
  }, []);

  const handleProgress = useCallback((value) => {
    progressRef.current = value;
  }, []);

  const handleHasAnimation = useCallback((value) => {
    setHasAnimation(value);
  }, []);

  useEffect(() => {
    if (!defaultClip) return;
    setActiveClip(defaultClip);
  }, [defaultClip]);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === '1') setMode('dance');
      if (event.key === '2') setMode('idle');
      if (event.key.toLowerCase() === 'r') {
        setReplaySignal((value) => value + 1);
      }
    };

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const statusLabel = mode === 'dance' ? 'Bailando' : 'Idle';

  return (
    <div className="app">
      <header className="panel">
        <div className="panel__title">
          <span className="tag">GLTF</span>
          <h1>Animaciones por Esqueleto</h1>
        </div>
        <p className="panel__text">
          Clip activo: <strong>{activeClip ?? 'cargando'}</strong>
        </p>
        <p className="panel__text">
          Estado: <strong>{statusLabel}</strong>
        </p>
        <div className="panel__buttons">
          <button
            type="button"
            className={mode === 'dance' ? 'is-active' : ''}
            onClick={() => setMode('dance')}
            disabled={!defaultClip}
          >
            Dance
          </button>
          <button
            type="button"
            className={mode === 'idle' ? 'is-active' : ''}
            onClick={() => setMode('idle')}
            disabled={!defaultClip}
          >
            Idle
          </button>
          <button
            type="button"
            onClick={() => setReplaySignal((value) => value + 1)}
            disabled={!defaultClip || mode !== 'dance'}
          >
            Replay
          </button>
        </div>
        
      </header>

      <Canvas shadows camera={{ position: [0, 1.5, 5.5], fov: 42 }}>
        <color attach="background" args={['#f5efe6']} />
        <ambientLight intensity={0.35} />
        <directionalLight
          position={[4, 6, 3]}
          intensity={1.1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <Suspense fallback={null}>
          <AnimatedCharacter
            activeClip={activeClip}
            mode={mode}
            replaySignal={replaySignal}
            onClips={handleClips}
            onProgress={handleProgress}
            onHasAnimation={handleHasAnimation}
          />
          <DanceMarker
            active={mode === 'dance'}
            hasAnimation={hasAnimation}
            progressRef={progressRef}
          />
          <Environment preset="sunset" />
        </Suspense>
        <mesh
          rotation={[-Math.PI / 2, 0, 0]}
          position={[0, 0, 0]}
          receiveShadow
        >
          <circleGeometry args={[4, 64]} />
          <meshStandardMaterial color="#e6ddcf" />
        </mesh>
        <ContactShadows
          position={[0, 0, 0]}
          opacity={0.35}
          scale={10}
          blur={2}
        />
        <OrbitControls
          enablePan
          enableZoom
          enableRotate
          minDistance={2}
          maxDistance={12}
          target={[0, 1, 0]}
        />
      </Canvas>
    </div>
  );
}
