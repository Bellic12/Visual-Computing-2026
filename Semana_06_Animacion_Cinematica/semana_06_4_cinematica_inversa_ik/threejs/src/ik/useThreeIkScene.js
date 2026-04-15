import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { clamp, solveCcd } from './ikSolver'
import {
  sceneDefaults,
  sceneColors,
  targetHeight,
  targetLimit,
  totalReach,
} from './sceneConfig'
import { disposeScene } from './sceneCleanup'
import {
  createArmRig,
  createEnvironment,
  createGuideLine,
  createTargetPath,
  createTargetRig,
} from './sceneObjects'

export function useThreeIkScene() {
  const mountRef = useRef(null)
  const iterationsRef = useRef(sceneDefaults.iterations)
  const influenceRef = useRef(sceneDefaults.influence)
  const autoTargetRef = useRef(sceneDefaults.autoTarget)
  const dragRef = useRef(false)
  const resetPoseRef = useRef(() => {})
  const randomizeTargetRef = useRef(() => {})

  const [iterations, setIterationsState] = useState(sceneDefaults.iterations)
  const [influence, setInfluenceState] = useState(sceneDefaults.influence)
  const [autoTarget, setAutoTargetState] = useState(sceneDefaults.autoTarget)
  const [metrics, setMetrics] = useState({
    distance: 0,
    chainLength: totalReach,
    targetDistance: 0,
    solved: false,
    reachable: true,
    mode: 'Manual target',
  })

  const setIterations = (value) => {
    iterationsRef.current = value
    setIterationsState(value)
  }

  const setInfluence = (value) => {
    influenceRef.current = value
    setInfluenceState(value)
  }

  const setAutoTarget = (valueOrUpdater) => {
    const nextValue =
      typeof valueOrUpdater === 'function'
        ? valueOrUpdater(autoTargetRef.current)
        : valueOrUpdater

    autoTargetRef.current = nextValue
    setAutoTargetState(nextValue)
  }

  useEffect(() => {
    const container = mountRef.current

    if (!container) {
      return undefined
    }

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100)
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    const clock = new THREE.Clock()
    const raycaster = new THREE.Raycaster()
    const pointer = new THREE.Vector2()
    const hitPoint = new THREE.Vector3()
    const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0)

    scene.background = new THREE.Color(sceneColors.background)
    scene.fog = new THREE.Fog(sceneColors.fog, 20, 50)
    camera.position.set(0, 10.5, 18)
    camera.lookAt(0, 1, 0)

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.1
    renderer.setSize(container.clientWidth, container.clientHeight, false)
    container.appendChild(renderer.domElement)

    const resizeScene = () => {
      const width = container.clientWidth || 1
      const height = container.clientHeight || 1

      camera.aspect = width / height
      camera.updateProjectionMatrix()
      renderer.setSize(width, height, false)
    }

    const resizeObserver = new ResizeObserver(resizeScene)
    resizeObserver.observe(container)

    createEnvironment(scene)
    const { root, joints, endEffector } = createArmRig(scene)
    const { target, targetRing, targetGlow } = createTargetRig(scene)
    const { positions: guidePositions, positionAttribute } = createGuideLine(scene)
    createTargetPath(scene, targetLimit)

    const placeTarget = (x, z) => {
      const clampedX = clamp(x, -targetLimit, targetLimit)
      const clampedZ = clamp(z, -targetLimit, targetLimit)

      target.position.set(clampedX, targetHeight, clampedZ)
      targetRing.position.copy(target.position)
      targetGlow.position.set(target.position.x, target.position.y + 0.4, target.position.z)
    }

    const resetPose = () => {
      joints.forEach((joint) => {
        joint.rotation.y = 0
      })

      root.rotation.y = 0
      root.position.set(0, 0, 0)
      placeTarget(4.7, 2.2)
    }

    const randomizeTarget = () => {
      const angle = Math.random() * Math.PI * 2
      const radius = 2.2 + Math.random() * (totalReach * 0.72)

      placeTarget(Math.cos(angle) * radius, Math.sin(angle) * radius)
    }

    const updatePointerTarget = (event) => {
      const rect = renderer.domElement.getBoundingClientRect()

      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

      raycaster.setFromCamera(pointer, camera)

      if (raycaster.ray.intersectPlane(groundPlane, hitPoint)) {
        placeTarget(hitPoint.x, hitPoint.z)
      }
    }

    const handlePointerDown = (event) => {
      if (event.button !== 0) {
        return
      }

      dragRef.current = true
      setAutoTarget(false)
      updatePointerTarget(event)
      renderer.domElement.setPointerCapture(event.pointerId)
    }

    const handlePointerMove = (event) => {
      if (dragRef.current) {
        updatePointerTarget(event)
      }
    }

    const handlePointerUp = (event) => {
      dragRef.current = false

      if (renderer.domElement.hasPointerCapture(event.pointerId)) {
        renderer.domElement.releasePointerCapture(event.pointerId)
      }
    }

    const handlePointerLeave = () => {
      dragRef.current = false
    }

    renderer.domElement.addEventListener('pointerdown', handlePointerDown)
    renderer.domElement.addEventListener('pointermove', handlePointerMove)
    renderer.domElement.addEventListener('pointerup', handlePointerUp)
    renderer.domElement.addEventListener('pointerleave', handlePointerLeave)
    renderer.domElement.addEventListener('pointercancel', handlePointerLeave)

    resetPoseRef.current = resetPose
    randomizeTargetRef.current = randomizeTarget
    resetPose()

    const targetPosition = new THREE.Vector3()
    const basePosition = new THREE.Vector3()

    const animate = () => {
      animationFrame = window.requestAnimationFrame(animate)

      const elapsedTime = clock.getElapsedTime()

      if (autoTargetRef.current && !dragRef.current) {
        const x = Math.cos(elapsedTime * 0.22) * 5.2
        const z = Math.sin(elapsedTime * 0.28) * 3.1 + Math.cos(elapsedTime * 0.16) * 0.9

        placeTarget(x, z)
      }

      target.material.emissiveIntensity = 1.05 + Math.sin(elapsedTime * 3.5) * 0.25
      targetRing.scale.setScalar(1 + Math.sin(elapsedTime * 2.4) * 0.06)

      target.getWorldPosition(targetPosition)

      const solveResult = solveCcd({
        root,
        joints,
        endEffector,
        targetPosition,
        iterations: iterationsRef.current,
        influence: influenceRef.current,
        threshold: 0.07,
      })

      root.updateMatrixWorld(true)
      root.getWorldPosition(basePosition)

      guidePositions[0] = basePosition.x
      guidePositions[1] = basePosition.y + 0.05
      guidePositions[2] = basePosition.z
      guidePositions[3] = targetPosition.x
      guidePositions[4] = targetPosition.y + 0.05
      guidePositions[5] = targetPosition.z
      positionAttribute.needsUpdate = true

      const targetDistance = basePosition.distanceTo(targetPosition)
      const reachable = targetDistance <= totalReach + 0.001

      setMetrics({
        distance: solveResult.distance,
        chainLength: totalReach,
        targetDistance,
        solved: solveResult.solved,
        reachable,
        mode: dragRef.current ? 'Dragging target' : autoTargetRef.current ? 'Auto target' : 'Manual target',
      })

      renderer.render(scene, camera)
    }

    let animationFrame = 0

    animate()

    return () => {
      window.cancelAnimationFrame(animationFrame)
      resizeObserver.disconnect()

      renderer.domElement.removeEventListener('pointerdown', handlePointerDown)
      renderer.domElement.removeEventListener('pointermove', handlePointerMove)
      renderer.domElement.removeEventListener('pointerup', handlePointerUp)
      renderer.domElement.removeEventListener('pointerleave', handlePointerLeave)
      renderer.domElement.removeEventListener('pointercancel', handlePointerLeave)

      disposeScene(scene)
      renderer.dispose()

      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement)
      }
    }
  }, [])

  return {
    mountRef,
    metrics,
    iterations,
    setIterations,
    influence,
    setInfluence,
    autoTarget,
    setAutoTarget,
    resetPose: () => resetPoseRef.current(),
    randomizeTarget: () => randomizeTargetRef.current(),
  }
}