import { Canvas, useFrame } from '@react-three/fiber'
import { Stars, OrbitControls } from '@react-three/drei'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './Juego.css'

const LANES = [4, 6]
const BASE_SPEED = 1.35
const MAX_SPEED = 2.6
const SPEED_STEP = 0.05
const SPAWN_MS = 1200

function Track() {
  return (
    <group>
      {LANES.map((radius) => (
        <mesh key={radius} rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[radius, 0.08, 16, 160]} />
          <meshStandardMaterial color="#2dd4bf" emissive="#22d3ee" emissiveIntensity={0.3} />
        </mesh>
      ))}

      <mesh>
        <sphereGeometry args={[1.4, 32, 32]} />
        <meshStandardMaterial color="#1c2541" emissive="#1a2a52" emissiveIntensity={0.6} />
      </mesh>
    </group>
  )
}

function Player({ lane }) {
  const radius = LANES[lane]
  return (
    <mesh position={[radius, 0.3, 0]}>
      <sphereGeometry args={[0.35, 20, 20]} />
      <meshStandardMaterial color="#ffb86b" emissive="#ffb86b" emissiveIntensity={0.8} />
    </mesh>
  )
}

function Obstacles({ obstacles }) {
  return (
    <group>
      {obstacles.map((obs) => {
        const radius = LANES[obs.lane]
        const x = Math.cos(obs.angle) * radius
        const z = Math.sin(obs.angle) * radius
        return (
          <mesh key={obs.id} position={[x, 0.3, z]}>
            <boxGeometry args={[0.5, 0.5, 0.5]} />
            <meshStandardMaterial color="#ff4d6d" emissive="#ff4d6d" emissiveIntensity={0.5} />
          </mesh>
        )
      })}
    </group>
  )
}

function RunnerWorld({ lane, obstacles, setObstacles, onScore, onGameOver, speedRef, paused, gameOver }) {
  useFrame((_, delta) => {
    if (paused || gameOver) return

    setObstacles((prev) => {
      let hit = false
      let passed = 0
      const next = []

      for (const obs of prev) {
        const nextAngle = obs.angle - speedRef.current * delta
        if (nextAngle < -0.5) {
          passed += 1
          continue
        }

        if (!hit && obs.lane === lane && Math.abs(nextAngle) < 0.14) {
          hit = true
        }

        next.push({ ...obs, angle: nextAngle })
      }

      if (passed > 0) {
        onScore(passed)
      }

      if (hit) {
        onGameOver()
        return prev
      }

      return next
    })
  })

  return (
    <>
      <ambientLight intensity={0.6} />
      <pointLight position={[6, 6, 6]} intensity={1.1} />
      <pointLight position={[-6, -4, -6]} intensity={0.6} color="#ffb86b" />
      <Track />
      <Player lane={lane} />
      <Obstacles obstacles={obstacles} />
    </>
  )
}

export default function Juego() {
  const navigate = useNavigate()
  const [lane, setLane] = useState(0)
  const [obstacles, setObstacles] = useState([])
  const [score, setScore] = useState(0)
  const [gameOver, setGameOver] = useState(false)
  const [paused, setPaused] = useState(false)
  const speedRef = useRef(BASE_SPEED)
  const nextId = useRef(1)

  const createObstacle = useCallback(() => {
    const id = nextId.current++
    return {
      id,
      lane: Math.random() > 0.5 ? 1 : 0,
      angle: Math.PI + Math.random() * 0.6,
    }
  }, [])

  const resetGame = useCallback(() => {
    setLane(0)
    setObstacles([])
    setScore(0)
    setGameOver(false)
    setPaused(false)
    speedRef.current = BASE_SPEED
  }, [])

  useEffect(() => {
    resetGame()
  }, [resetGame])

  useEffect(() => {
    if (gameOver || paused) return

    const interval = setInterval(() => {
      setObstacles((prev) => [...prev, createObstacle()])
    }, SPAWN_MS)

    return () => clearInterval(interval)
  }, [gameOver, paused, createObstacle])

  const handleScore = useCallback((passed) => {
    setScore((prev) => {
      const nextScore = prev + passed
      speedRef.current = Math.min(BASE_SPEED + nextScore * SPEED_STEP, MAX_SPEED)
      return nextScore
    })
  }, [])

  const handleGameOver = useCallback(() => {
    setGameOver(true)
  }, [])

  useEffect(() => {
    const handleKey = (event) => {
      if (gameOver && event.code !== 'KeyR' && event.code !== 'Escape') return

      switch (event.code) {
        case 'ArrowLeft':
        case 'KeyA':
          setLane(0)
          break
        case 'ArrowRight':
        case 'KeyD':
          setLane(1)
          break
        case 'Space':
          setPaused((prev) => !prev)
          break
        case 'KeyR':
          resetGame()
          break
        case 'Escape':
          navigate('/')
          break
      }
    }

    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [gameOver, resetGame, navigate])

  return (
    <div className="scene-root">
      <Canvas className="scene-canvas" camera={{ position: [0, 8, 10], fov: 50 }}>
        <RunnerWorld
          lane={lane}
          obstacles={obstacles}
          setObstacles={setObstacles}
          onScore={handleScore}
          onGameOver={handleGameOver}
          speedRef={speedRef}
          paused={paused}
          gameOver={gameOver}
        />
        <Stars radius={70} depth={60} count={1000} factor={4} fade speed={1} />
        <OrbitControls enablePan={false} enableZoom={false} enableRotate={false} />
      </Canvas>

      <div className="game-overlay">
        <div className="game-hud">
          <div className="hud-title">Orbital Runner 3D</div>
          <div className="hud-stats">
            <span>Score: {score}</span>
            <span>Speed: {speedRef.current.toFixed(2)}</span>
            <span>Lane: {lane === 0 ? 'Inner' : 'Outer'}</span>
          </div>
        </div>

        <div className="game-controls">
          <span>A / Left: inner lane</span>
          <span>D / Right: outer lane</span>
          <span>Space: pause</span>
          <span>R: reset</span>
          <span>Esc: menu</span>
        </div>
      </div>

      {paused && !gameOver && (
        <div className="game-modal">
          <div className="modal-card">
            <h2>Pause</h2>
            <p>Press Space to resume.</p>
            <button className="btn btn-primary" onClick={() => setPaused(false)}>
              Resume
            </button>
          </div>
        </div>
      )}

      {gameOver && (
        <div className="game-modal">
          <div className="modal-card">
            <h2>Game Over</h2>
            <p>Your score: {score}</p>
            <div className="modal-actions">
              <button className="btn btn-primary" onClick={resetGame}>
                Restart
              </button>
              <button className="btn btn-ghost" onClick={() => navigate('/')}> 
                Back to menu
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
