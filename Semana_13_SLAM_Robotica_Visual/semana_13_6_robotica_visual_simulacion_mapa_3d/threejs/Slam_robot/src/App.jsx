import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import './App.css'

function App() {
  const containerRef = useRef(null)
  const sceneRef = useRef(null)
  const robotRef = useRef(null)
  const raycasterRef = useRef(null)
  const arrowHelpersRef = useRef([])
  const trajectoryRef = useRef(null)
  const trajectoryPointsRef = useRef([])
  const animationIdRef = useRef(null)
  const keysRef = useRef({ w: false, a: false, s: false, d: false })

  // Use refs for runtime values that change during animation
  const configRef = useRef({
    isRunning: true,
    speed: 0.05,
    turnSpeed: 0.05,
    detectionDistance: 4,
    mode: 'auto'
  })

  // UI state (for display only)
  const [isRunning, setIsRunning] = useState(true)
  const [speed, setSpeed] = useState(0.05)
  const [turnSpeed, setTurnSpeed] = useState(0.05)
  const [detectionDistance, setDetectionDistance] = useState(4)
  const [mode, setMode] = useState('auto')

  // Sync UI state to refs
  useEffect(() => {
    configRef.current.isRunning = isRunning
  }, [isRunning])

  useEffect(() => {
    configRef.current.speed = speed
  }, [speed])

  useEffect(() => {
    configRef.current.turnSpeed = turnSpeed
  }, [turnSpeed])

  useEffect(() => {
    configRef.current.detectionDistance = detectionDistance
  }, [detectionDistance])

  useEffect(() => {
    configRef.current.mode = mode
  }, [mode])

  useEffect(() => {
    if (!containerRef.current) return

    const container = containerRef.current

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x1a1a2e)
    sceneRef.current = scene

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    )
    camera.position.set(0, 15, 15)
    camera.lookAt(0, 0, 0)

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(container.clientWidth, container.clientHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    container.appendChild(renderer.domElement)

    // OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
    directionalLight.position.set(10, 20, 10)
    scene.add(directionalLight)

    // Floor
    const floorGeometry = new THREE.PlaneGeometry(30, 30)
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x2d2d44,
      side: THREE.DoubleSide
    })
    const floor = new THREE.Mesh(floorGeometry, floorMaterial)
    floor.rotation.x = -Math.PI / 2
    floor.receiveShadow = true
    scene.add(floor)

    // Grid helper
    const gridHelper = new THREE.GridHelper(30, 30, 0x4a4a6a, 0x3a3a5a)
    scene.add(gridHelper)

    // Robot (blue box)
    const robotGeometry = new THREE.BoxGeometry(1, 1, 1)
    const robotMaterial = new THREE.MeshStandardMaterial({ color: 0x00aaff })
    const robot = new THREE.Mesh(robotGeometry, robotMaterial)
    robot.position.set(0, 0.5, 10)
    robot.castShadow = true
    scene.add(robot)
    robotRef.current = robot

    // Robot direction indicator
    const directionGeometry = new THREE.ConeGeometry(0.2, 0.5, 8)
    const directionMaterial = new THREE.MeshStandardMaterial({ color: 0xffaa00 })
    const directionIndicator = new THREE.Mesh(directionGeometry, directionMaterial)
    directionIndicator.rotation.x = Math.PI / 2
    directionIndicator.position.set(0, 0.5, 0.6)
    robot.add(directionIndicator)

    // Obstacles
    const obstacles = []
    const obstaclePositions = [
      { x: -5, z: 5 },
      { x: 5, z: 5 },
      { x: -5, z: -5 },
      { x: 5, z: -5 },
      { x: 0, z: 0 },
      { x: -8, z: 8 },
      { x: 8, z: 8 },
      { x: -8, z: -2 },
      { x: 8, z: -2 },
    ]

    const obstacleGeometry = new THREE.BoxGeometry(2, 2, 2)
    const obstacleMaterial = new THREE.MeshStandardMaterial({ color: 0xff6b6b })

    obstaclePositions.forEach((pos) => {
      const obstacle = new THREE.Mesh(obstacleGeometry, obstacleMaterial)
      obstacle.position.set(pos.x, 1, pos.z)
      obstacle.castShadow = true
      obstacle.receiveShadow = true
      scene.add(obstacle)
      obstacles.push(obstacle)
    })

    // Walls (boundaries as obstacles)
    const wallHeight = 3
    const wallThickness = 0.5
    const wallLength = 30
    const wallDistance = 13
    const wallMaterial = new THREE.MeshStandardMaterial({ color: 0x8866aa })

    const walls = [
      { x: 0, z: wallDistance, w: wallLength, h: wallThickness },   // north
      { x: 0, z: -wallDistance, w: wallLength, h: wallThickness },  // south
      { x: wallDistance, z: 0, w: wallThickness, h: wallLength }, // east
      { x: -wallDistance, z: 0, w: wallThickness, h: wallLength }, // west
    ]

    walls.forEach((wall) => {
      const wallGeo = new THREE.BoxGeometry(wall.w, wallHeight, wall.h)
      const wallMesh = new THREE.Mesh(wallGeo, wallMaterial)
      wallMesh.position.set(wall.x, wallHeight / 2, wall.z)
      wallMesh.castShadow = true
      wallMesh.receiveShadow = true
      scene.add(wallMesh)
      obstacles.push(wallMesh)
    })

    // Raycaster
    const raycaster = new THREE.Raycaster()
    raycasterRef.current = { raycaster, obstacles }

    // Trajectory line
    const trajectoryMaterial = new THREE.LineBasicMaterial({ color: 0x00ff88 })
    const trajectoryGeometry = new THREE.BufferGeometry()
    const trajectoryLine = new THREE.Line(trajectoryGeometry, trajectoryMaterial)
    scene.add(trajectoryLine)
    trajectoryRef.current = trajectoryLine

    // Arrow helpers for ray visualization (only front and sides, no back)
    // These will be children of robot so they rotate with it
    const arrowHelpers = []
    const numRays = 5
    for (let i = 0; i < numRays; i++) {
      const angleOffset = (i - Math.floor(numRays / 2)) * (Math.PI / 4) // -90°, -45°, 0°, 45°, 90°
      const direction = new THREE.Vector3(
        Math.sin(angleOffset),
        0,
        -Math.cos(angleOffset)
      ).normalize()

      // Position relative to robot center
      const origin = new THREE.Vector3(0, 0, 0)

      const arrowHelper = new THREE.ArrowHelper(
        direction,
        origin,
        2,
        0xffff00,
        0.3,
        0.2
      )
      robot.add(arrowHelper)
      arrowHelpers.push(arrowHelper)
    }
    arrowHelpersRef.current = arrowHelpers

    const handleKeyDown = (e) => {
      const key = e.key.toLowerCase()
      if (key === 'w') keysRef.current.w = true
      if (key === 'a') keysRef.current.a = true
      if (key === 's') keysRef.current.s = true
      if (key === 'd') keysRef.current.d = true
      if (key === 'm') {
        setMode((prev) => (prev === 'auto' ? 'manual' : 'auto'))
      }
    }

    const handleKeyUp = (e) => {
      const key = e.key.toLowerCase()
      if (key === 'w') keysRef.current.w = false
      if (key === 'a') keysRef.current.a = false
      if (key === 's') keysRef.current.s = false
      if (key === 'd') keysRef.current.d = false
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)

    // Animation loop
    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate)

      if (!robotRef.current || !raycasterRef.current) return

      const robot = robotRef.current
      const { raycaster: rc, obstacles } = raycasterRef.current
      const config = configRef.current
      const keys = keysRef.current

      // Update arrow length based on detection distance
      arrowHelpersRef.current.forEach((arrow) => {
        arrow.setLength(config.detectionDistance, 0.3, 0.2)
      })

      if (config.isRunning && config.mode === 'auto') {
        // Only check front and sides (no back sensors)
        // Note: robot.rotation.y is already applied to arrows since they're children
        // So we use base angles only
        const frontAngles = [0, Math.PI / 4, -Math.PI / 4]
        let obstacleInFront = false
        let closestDist = Infinity

        for (const angleOffset of frontAngles) {
          const direction = new THREE.Vector3(
            Math.sin(angleOffset),
            0,
            -Math.cos(angleOffset)
          ).normalize()

          // Rotate direction by robot's current rotation
          direction.applyAxisAngle(new THREE.Vector3(0, 1, 0), robot.rotation.y)

          rc.set(robot.position.clone(), direction)
          const intersects = rc.intersectObjects(obstacles)

          if (intersects.length > 0 && intersects[0].distance < config.detectionDistance) {
            obstacleInFront = true
            if (intersects[0].distance < closestDist) {
              closestDist = intersects[0].distance
            }
          }
        }

        if (obstacleInFront) {
          // Turn until path is clear
          robot.rotation.y += config.turnSpeed * 1.5
        } else {
          // Move forward only when path is clear
          robot.position.z -= config.speed * Math.cos(robot.rotation.y)
          robot.position.x -= config.speed * Math.sin(robot.rotation.y)
        }
      } else if (config.mode === 'manual') {
        // Manual control
        if (keys.w) {
          robot.position.z -= config.speed * Math.cos(robot.rotation.y)
          robot.position.x -= config.speed * Math.sin(robot.rotation.y)
        }
        if (keys.s) {
          robot.position.z += config.speed * Math.cos(robot.rotation.y)
          robot.position.x += config.speed * Math.sin(robot.rotation.y)
        }
        if (keys.a) {
          robot.rotation.y += config.turnSpeed
        }
        if (keys.d) {
          robot.rotation.y -= config.turnSpeed
        }
      }

      // Update trajectory
      trajectoryPointsRef.current.push(robot.position.clone())
      if (trajectoryPointsRef.current.length > 500) {
        trajectoryPointsRef.current.shift()
      }

      const points = trajectoryPointsRef.current
      const geometry = trajectoryRef.current.geometry
      geometry.setFromPoints(points)

      // Update controls
      controls.update()

      // Render
      renderer.render(scene, camera)
    }

    animate()

    // Handle resize
    const handleResize = () => {
      camera.aspect = container.clientWidth / container.clientHeight
      camera.updateProjectionMatrix()
      renderer.setSize(container.clientWidth, container.clientHeight)
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
      window.removeEventListener('resize', handleResize)
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current)
      }
      renderer.dispose()
      container.removeChild(renderer.domElement)
    }
  }, [])

  return (
    <div className="app">
      <div ref={containerRef} className="canvas-container" />

      <div className="controls-panel">
        <h2>SLAM Robot Control</h2>

        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={isRunning}
              onChange={(e) => setIsRunning(e.target.checked)}
            />
            Auto Mode
          </label>
        </div>

        <div className="control-group">
          <label>Mode: {mode.toUpperCase()}</label>
          <p className="hint">Press 'M' to toggle</p>
        </div>

        <div className="control-group">
          <label>Speed: {speed.toFixed(3)}</label>
          <input
            type="range"
            min="0.01"
            max="0.2"
            step="0.01"
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
          />
        </div>

        <div className="control-group">
          <label>Turn Speed: {turnSpeed.toFixed(3)}</label>
          <input
            type="range"
            min="0.01"
            max="0.15"
            step="0.01"
            value={turnSpeed}
            onChange={(e) => setTurnSpeed(parseFloat(e.target.value))}
          />
        </div>

        <div className="control-group">
          <label>Detection Distance: {detectionDistance}</label>
          <input
            type="range"
            min="1"
            max="10"
            step="0.5"
            value={detectionDistance}
            onChange={(e) => setDetectionDistance(parseFloat(e.target.value))}
          />
        </div>

        <div className="instructions">
          <h3>Controls</h3>
          <p><strong>W</strong> - Forward</p>
          <p><strong>S</strong> - Backward</p>
          <p><strong>A</strong> - Turn Left</p>
          <p><strong>D</strong> - Turn Right</p>
          <p><strong>M</strong> - Toggle Auto/Manual</p>
          <p><strong>Mouse</strong> - Rotate Camera</p>
        </div>
      </div>

      <div className="legend">
        <div className="legend-item">
          <div className="color-box robot"></div>
          <span>Robot</span>
        </div>
        <div className="legend-item">
          <div className="color-box obstacle"></div>
          <span>Obstacle</span>
        </div>
        <div className="legend-item">
          <div className="color-box trajectory"></div>
          <span>Trajectory</span>
        </div>
        <div className="legend-item">
          <div className="color-box ray"></div>
          <span>Ray (sensor)</span>
        </div>
      </div>
    </div>
  )
}

export default App