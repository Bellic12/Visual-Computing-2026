import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Line } from '@react-three/drei'
import * as THREE from 'three'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js'
import { SCENE_POINTS } from './constants'

const RADIAL_DISTORTION_SHADER = {
  uniforms: {
    tDiffuse: { value: null },
    k1: { value: 0 },
    k2: { value: 0 },
    enabled: { value: 0 }
  },
  vertexShader: `
    varying vec2 vUv;

    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float k1;
    uniform float k2;
    uniform float enabled;
    varying vec2 vUv;

    void main() {
      if (enabled < 0.5) {
        gl_FragColor = texture2D(tDiffuse, vUv);
        return;
      }

      vec2 p = vUv * 2.0 - 1.0;
      float r2 = dot(p, p);
      float factor = 1.0 + k1 * r2 + k2 * r2 * r2;

      vec2 sampled = p / factor;
      vec2 uv = sampled * 0.5 + 0.5;

      if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
      }

      gl_FragColor = texture2D(tDiffuse, uv);
    }
  `
}

function SceneObjects() {
  return (
    <>
      <ambientLight intensity={0.45} />
      <directionalLight position={[8, 10, 6]} intensity={1.25} />
      <pointLight position={[-8, 4, -5]} intensity={0.7} color="#ff9f1c" />

      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.6, -6]} receiveShadow>
        <planeGeometry args={[40, 40]} />
        <meshStandardMaterial color="#ffffff" metalness={0.1} roughness={0.85} />
      </mesh>

      <gridHelper args={[32, 32, '#4aa3ff', '#16324f']} position={[0, -1.59, -6]} />
      <axesHelper args={[3.5]} />

      <mesh position={[0, 0, -6]}>
        <boxGeometry args={[2, 2, 2]} />
        <meshStandardMaterial color="#4062bb" metalness={0.2} roughness={0.45} />
      </mesh>

      <mesh position={[-4, 1.25, -9]}>
        <coneGeometry args={[1.1, 2.2, 24]} />
        <meshStandardMaterial color="#f25f5c" metalness={0.15} roughness={0.5} />
      </mesh>

      <mesh position={[4, -0.15, -4.5]}>
        <torusKnotGeometry args={[0.8, 0.25, 120, 16]} />
        <meshStandardMaterial color="#70c1b3" metalness={0.35} roughness={0.35} />
      </mesh>

      {SCENE_POINTS.map((point) => (
        <mesh key={point.id} position={point.position}>
          <sphereGeometry args={[0.18, 20, 20]} />
          <meshStandardMaterial color={point.color} emissive={point.color} emissiveIntensity={0.5} />
        </mesh>
      ))}
    </>
  )
}

function VirtualCameraModel({ camera }) {
  const groupRef = useRef(null)

  useFrame(() => {
    if (!camera || !groupRef.current) {
      return
    }

    groupRef.current.position.copy(camera.position)
    groupRef.current.quaternion.copy(camera.quaternion)
  })

  return (
    <group ref={groupRef}>
      <mesh>
        <boxGeometry args={[0.6, 0.36, 0.34]} />
        <meshStandardMaterial color="#e8edf7" metalness={0.25} roughness={0.45} />
      </mesh>
      <mesh position={[0, 0, -0.28]}>
        <coneGeometry args={[0.12, 0.32, 20]} />
        <meshStandardMaterial color="#111827" metalness={0.1} roughness={0.9} />
      </mesh>
    </group>
  )
}

function FrustumVolume({ camera, cameraState }) {
  const groupRef = useRef(null)

  const { faces, edges } = useMemo(() => {
    const fovRad = THREE.MathUtils.degToRad(cameraState.fov)
    const nearHeight = 2 * Math.tan(fovRad * 0.5) * cameraState.near
    const nearWidth = nearHeight * cameraState.aspect
    const farHeight = 2 * Math.tan(fovRad * 0.5) * cameraState.far
    const farWidth = farHeight * cameraState.aspect

    const nTL = [-nearWidth * 0.5, nearHeight * 0.5, -cameraState.near]
    const nTR = [nearWidth * 0.5, nearHeight * 0.5, -cameraState.near]
    const nBR = [nearWidth * 0.5, -nearHeight * 0.5, -cameraState.near]
    const nBL = [-nearWidth * 0.5, -nearHeight * 0.5, -cameraState.near]

    const fTL = [-farWidth * 0.5, farHeight * 0.5, -cameraState.far]
    const fTR = [farWidth * 0.5, farHeight * 0.5, -cameraState.far]
    const fBR = [farWidth * 0.5, -farHeight * 0.5, -cameraState.far]
    const fBL = [-farWidth * 0.5, -farHeight * 0.5, -cameraState.far]

    const triangles = [
      ...nTL, ...nTR, ...nBR,
      ...nTL, ...nBR, ...nBL,
      ...fTL, ...fBR, ...fTR,
      ...fTL, ...fBL, ...fBR,
      ...nTL, ...nBL, ...fBL,
      ...nTL, ...fBL, ...fTL,
      ...nTR, ...fTR, ...fBR,
      ...nTR, ...fBR, ...nBR,
      ...nTL, ...fTL, ...fTR,
      ...nTL, ...fTR, ...nTR,
      ...nBL, ...nBR, ...fBR,
      ...nBL, ...fBR, ...fBL
    ]

    const edgeSegments = [
      [nTL, nTR], [nTR, nBR], [nBR, nBL], [nBL, nTL],
      [fTL, fTR], [fTR, fBR], [fBR, fBL], [fBL, fTL],
      [nTL, fTL], [nTR, fTR], [nBR, fBR], [nBL, fBL]
    ]

    return { faces: triangles, edges: edgeSegments }
  }, [cameraState.aspect, cameraState.far, cameraState.fov, cameraState.near])

  useFrame(() => {
    if (!camera || !groupRef.current) {
      return
    }

    groupRef.current.position.copy(camera.position)
    groupRef.current.quaternion.copy(camera.quaternion)
  })

  if (!camera) {
    return null
  }

  return (
    <group ref={groupRef}>
      <mesh renderOrder={1}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[new Float32Array(faces), 3]} />
        </bufferGeometry>
        <meshBasicMaterial
          color="#7dd3fc"
          transparent
          opacity={0.09}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>

      {edges.map((segment, index) => (
        <Line
          key={`frustum-edge-${index}`}
          points={segment}
          color="#80d8ff"
          transparent
          opacity={0.95}
          lineWidth={1}
        />
      ))}
    </group>
  )
}

function FrustumAndRays({ camera, cameraState }) {
  const helperRef = useRef(null)

  useFrame(() => {
    if (helperRef.current) {
      helperRef.current.update()
    }
  })

  const cameraPosition = useMemo(
    () => [cameraState.x, cameraState.y, cameraState.z],
    [cameraState.x, cameraState.y, cameraState.z]
  )

  if (!camera) {
    return null
  }

  return (
    <>
      <cameraHelper ref={helperRef} args={[camera]} />
      <VirtualCameraModel camera={camera} />
      <FrustumVolume camera={camera} cameraState={cameraState} />

      {SCENE_POINTS.map((point) => (
        <Line
          key={`ray-${point.id}`}
          points={[cameraPosition, point.position]}
          color="#7dd3fc"
          transparent
          opacity={0.5}
          lineWidth={1}
        />
      ))}
    </>
  )
}

function RadialDistortionEffect({ distortionState, viewMode }) {
  const { gl, scene, camera, size } = useThree()
  const composerRef = useRef(null)
  const renderPassRef = useRef(null)
  const shaderPassRef = useRef(null)

  useEffect(() => {
    const composer = new EffectComposer(gl)
    const renderPass = new RenderPass(scene, camera)
    const shaderPass = new ShaderPass(RADIAL_DISTORTION_SHADER)

    composer.setSize(size.width, size.height)
    composer.addPass(renderPass)
    composer.addPass(shaderPass)

    composerRef.current = composer
    renderPassRef.current = renderPass
    shaderPassRef.current = shaderPass

    return () => {
      composer.dispose()
      composerRef.current = null
      renderPassRef.current = null
      shaderPassRef.current = null
    }
  }, [camera, gl, scene])

  useEffect(() => {
    if (composerRef.current) {
      composerRef.current.setSize(size.width, size.height)
    }
  }, [size.height, size.width])

  useFrame((state) => {
    const composer = composerRef.current
    const renderPass = renderPassRef.current
    const shaderPass = shaderPassRef.current

    if (!composer || !renderPass || !shaderPass) {
      return
    }

    renderPass.camera = state.camera
    shaderPass.uniforms.k1.value = distortionState.k1
    shaderPass.uniforms.k2.value = distortionState.k2
    shaderPass.uniforms.enabled.value =
      distortionState.enabled && distortionState.applyTo3d && viewMode === 'camera' ? 1 : 0

    composer.render()
  }, 1)

  return null
}

function LabSceneContent({ cameraState, distortionState, viewMode }) {
  const [observerCamera, setObserverCamera] = useState(null)
  const [virtualCamera, setVirtualCamera] = useState(null)
  const virtualCameraRef = useRef(null)
  const { set } = useThree()

  const pitch = THREE.MathUtils.degToRad(cameraState.pitch)
  const yaw = THREE.MathUtils.degToRad(cameraState.yaw)

  const handleObserverCameraRef = useCallback((cameraRef) => {
    if (cameraRef) {
      setObserverCamera(cameraRef)
    }
  }, [])

  const handleVirtualCameraRef = useCallback((cameraRef) => {
    virtualCameraRef.current = cameraRef
    if (cameraRef) {
      setVirtualCamera(cameraRef)
    }
  }, [])

  useEffect(() => {
    const cameraRef = virtualCameraRef.current
    if (!cameraRef) {
      return
    }

    cameraRef.rotation.order = 'YXZ'
    cameraRef.position.set(cameraState.x, cameraState.y, cameraState.z)
    cameraRef.rotation.set(pitch, yaw, 0)
    cameraRef.fov = cameraState.fov
    cameraRef.aspect = cameraState.aspect
    cameraRef.near = cameraState.near
    cameraRef.far = cameraState.far
    cameraRef.updateProjectionMatrix()
    cameraRef.updateMatrixWorld(true)
  }, [cameraState, pitch, yaw])

  useEffect(() => {
    const activeCamera = viewMode === 'camera' ? virtualCamera : observerCamera

    if (activeCamera) {
      set({ camera: activeCamera })
    }
  }, [observerCamera, set, viewMode, virtualCamera])

  return (
    <>
      <PerspectiveCamera
        ref={handleObserverCameraRef}
        position={[13, 8, 11]}
        fov={48}
        near={0.1}
        far={120}
      />

      <PerspectiveCamera
        ref={handleVirtualCameraRef}
        position={[cameraState.x, cameraState.y, cameraState.z]}
        rotation={[pitch, yaw, 0]}
        fov={cameraState.fov}
        near={cameraState.near}
        far={cameraState.far}
        aspect={cameraState.aspect}
      />

      <SceneObjects />
      <RadialDistortionEffect distortionState={distortionState} viewMode={viewMode} />

      {viewMode === 'observer' ? (
        <>
          <FrustumAndRays camera={virtualCamera} cameraState={cameraState} />
          <OrbitControls target={[0, 0, -6]} maxDistance={38} minDistance={5} />
        </>
      ) : (
        <OrbitControls enabled={false} />
      )}
    </>
  )
}

export function CameraLabScene({ cameraState, distortionState, viewMode }) {
  return (
    <div className="canvas-shell">
      <Canvas shadows gl={{ antialias: true }}>
        <color attach="background" args={['#b1b1b1']} />
        <LabSceneContent
          cameraState={cameraState}
          distortionState={distortionState}
          viewMode={viewMode}
        />
      </Canvas>
    </div>
  )
}
