import { useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'
import './App.css'

const SOCKET_URL = 'ws://localhost:8765'

const COLOR_MAP = {
  red: '#ef4444',
  green: '#22c55e',
  blue: '#3b82f6',
}

function ReactiveSphere({ target }) {
  const meshRef = useRef(null)
  const targetColor = useMemo(
    () => new THREE.Color(COLOR_MAP[target.color] ?? '#f59e0b'),
    [target.color],
  )

  useFrame((_, delta) => {
    if (!meshRef.current) {
      return
    }

    meshRef.current.position.x = THREE.MathUtils.lerp(
      meshRef.current.position.x,
      target.x,
      Math.min(1, delta * 3),
    )
    meshRef.current.position.y = THREE.MathUtils.lerp(
      meshRef.current.position.y,
      target.y,
      Math.min(1, delta * 3),
    )

    meshRef.current.material.color.lerp(targetColor, Math.min(1, delta * 5))
  })

  return (
    <mesh ref={meshRef} castShadow>
      <sphereGeometry args={[0.5, 48, 48]} />
      <meshStandardMaterial color={COLOR_MAP[target.color] ?? '#f59e0b'} />
    </mesh>
  )
}

function App() {
  const [liveData, setLiveData] = useState({ x: 0, y: 0, color: 'blue' })
  const [socketState, setSocketState] = useState('connecting')
  const [lastMessageAt, setLastMessageAt] = useState(null)

  useEffect(() => {
    let socket = null
    let reconnectTimer = null
    let cancelled = false

    const connect = () => {
      if (cancelled) {
        return
      }

      setSocketState('connecting')
      socket = new WebSocket(SOCKET_URL)

      socket.onopen = () => {
        setSocketState('connected')
      }

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data)
          setLiveData({
            x: Number(payload.x) || 0,
            y: Number(payload.y) || 0,
            color: payload.color || 'blue',
          })
          setLastMessageAt(new Date())
        } catch {
          setSocketState('error')
        }
      }

      socket.onerror = () => {
        setSocketState('error')
      }

      socket.onclose = () => {
        if (cancelled) {
          return
        }

        setSocketState('disconnected')
        reconnectTimer = window.setTimeout(connect, 1500)
      }
    }

    connect()

    return () => {
      cancelled = true
      if (reconnectTimer) {
        window.clearTimeout(reconnectTimer)
      }
      if (socket) {
        socket.close()
      }
    }
  }, [])

  const lastMessageText = lastMessageAt
    ? lastMessageAt.toLocaleTimeString()
    : 'Sin mensajes todavía'

  return (
    <div className="app-shell">
      <header className="hud">
        <h1>Taller 7.12: WebSockets + Three.js</h1>
        <div className="hud-grid">
          <p>
            Estado: <strong className={`status ${socketState}`}>{socketState}</strong>
          </p>
          <p>
            x: <strong>{liveData.x.toFixed(3)}</strong>
          </p>
          <p>
            y: <strong>{liveData.y.toFixed(3)}</strong>
          </p>
          <p>
            color: <strong>{liveData.color}</strong>
          </p>
          <p>
            ultimo mensaje: <strong>{lastMessageText}</strong>
          </p>
        </div>
      </header>

      <Canvas className="scene" shadows camera={{ position: [0, 0, 8], fov: 55 }}>
        <color attach="background" args={['#10131f']} />
        <fog attach="fog" args={['#10131f', 8, 20]} />
        <ambientLight intensity={0.35} />
        <directionalLight position={[4, 6, 5]} intensity={1.1} castShadow />
        <pointLight position={[-4, -2, 2]} intensity={20} color="#f59e0b" />

        <ReactiveSphere target={liveData} />

        <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -2.4, 0]}>
          <planeGeometry args={[18, 18]} />
          <meshStandardMaterial color="#1b2440" />
        </mesh>

        <gridHelper args={[20, 20, '#334155', '#1f2937']} position={[0, -2.39, 0]} />
        <axesHelper args={[2.4]} position={[-6.5, -1.8, 0]} />
        <OrbitControls enablePan={false} minDistance={5} maxDistance={12} />
      </Canvas>
    </div>
  )
}

export default App
