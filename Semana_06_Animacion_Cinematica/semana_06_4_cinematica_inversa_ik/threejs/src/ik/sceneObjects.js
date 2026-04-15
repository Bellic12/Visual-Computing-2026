import * as THREE from 'three'
import { sceneColors, segmentLengths } from './sceneConfig'

function createSegmentMaterial(baseColor, emissiveColor) {
  return new THREE.MeshStandardMaterial({
    color: baseColor,
    emissive: emissiveColor,
    emissiveIntensity: 0.2,
    roughness: 0.35,
    metalness: 0.28,
  })
}

export function createEnvironment(scene) {
  const ambientLight = new THREE.AmbientLight(sceneColors.ambient, 1.2)
  const keyLight = new THREE.DirectionalLight(sceneColors.keyLight, 2.4)
  const rimLight = new THREE.DirectionalLight(sceneColors.rimLight, 0.7)
  const grid = new THREE.GridHelper(34, 34, sceneColors.gridMajor, sceneColors.gridMinor)
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(34, 34),
    new THREE.MeshStandardMaterial({
      color: sceneColors.floor,
      roughness: 1,
      metalness: 0,
      transparent: true,
      opacity: 0.92,
    }),
  )

  keyLight.position.set(8, 15, 10)
  rimLight.position.set(-10, 6, -8)
  grid.position.y = 0.001
  floor.rotation.x = -Math.PI / 2

  scene.add(ambientLight, keyLight, rimLight, grid, floor)

  return { ambientLight, keyLight, rimLight, grid, floor }
}

export function createArmRig(scene) {
  const root = new THREE.Group()
  const rootMarker = new THREE.Mesh(
    new THREE.CylinderGeometry(0.18, 0.22, 0.18, 18),
    new THREE.MeshStandardMaterial({
      color: sceneColors.root,
      emissive: sceneColors.rootEmissive,
      emissiveIntensity: 0.35,
      roughness: 0.4,
      metalness: 0.15,
    }),
  )

  rootMarker.position.y = 0.09
  root.add(rootMarker)

  const joints = []
  let anchor = root

  segmentLengths.forEach((length, index) => {
    const joint = new THREE.Group()
    const segmentHue = 0.55 - index * 0.06
    const segment = new THREE.Mesh(
      new THREE.BoxGeometry(length, 0.42, 0.82),
      createSegmentMaterial(
        new THREE.Color().setHSL(segmentHue, 0.42, 0.56),
        new THREE.Color().setHSL(segmentHue, 0.7, 0.16),
      ),
    )
    const jointKnob = new THREE.Mesh(
      new THREE.SphereGeometry(0.2, 24, 24),
      new THREE.MeshStandardMaterial({
        color: sceneColors.segmentBase,
        emissive: 0x0a1220,
        emissiveIntensity: 0.22,
        roughness: 0.45,
        metalness: 0.25,
      }),
    )
    const nextAnchor = new THREE.Group()

    segment.position.set(length / 2, 0.2, 0)
    jointKnob.position.set(0, 0.2, 0)
    nextAnchor.position.x = length

    joint.add(segment, jointKnob, nextAnchor)
    anchor.add(joint)

    joints.push(joint)
    anchor = nextAnchor
  })

  const endEffector = new THREE.Mesh(
    new THREE.SphereGeometry(0.34, 28, 28),
    new THREE.MeshStandardMaterial({
      color: 0xffd166,
      emissive: 0x9b5300,
      emissiveIntensity: 0.9,
      roughness: 0.22,
      metalness: 0.12,
    }),
  )
  endEffector.position.y = 0.2
  anchor.add(endEffector)

  scene.add(root)

  return { root, joints, endEffector }
}

export function createTargetRig(scene) {
  const target = new THREE.Mesh(
    new THREE.SphereGeometry(0.42, 28, 28),
    new THREE.MeshStandardMaterial({
      color: sceneColors.target,
      emissive: sceneColors.targetEmissive,
      emissiveIntensity: 1.35,
      roughness: 0.18,
      metalness: 0.15,
    }),
  )
  const targetRing = new THREE.Mesh(
    new THREE.TorusGeometry(0.7, 0.05, 16, 40),
    new THREE.MeshStandardMaterial({
      color: sceneColors.targetRing,
      emissive: sceneColors.targetRingEmissive,
      emissiveIntensity: 0.85,
      roughness: 0.4,
      metalness: 0.2,
    }),
  )
  const targetGlow = new THREE.PointLight(sceneColors.target, 2.4, 12, 2)

  targetRing.rotation.x = Math.PI / 2
  targetRing.position.y = 0.02
  targetGlow.position.set(0, 0.8, 0)
  target.add(targetGlow)
  scene.add(target, targetRing)

  return { target, targetRing, targetGlow }
}

export function createGuideLine(scene) {
  const positions = new Float32Array(6)
  const geometry = new THREE.BufferGeometry()

  const positionAttribute = new THREE.BufferAttribute(positions, 3)
  geometry.setAttribute('position', positionAttribute)

  const guideLine = new THREE.Line(
    geometry,
    new THREE.LineBasicMaterial({
      color: sceneColors.guide,
      transparent: true,
      opacity: 0.85,
    }),
  )

  scene.add(guideLine)

  return { guideLine, positions, positionAttribute }
}

export function createTargetPath(scene, targetLimit) {
  const points = [
    new THREE.Vector3(-targetLimit, 0.02, 0),
    new THREE.Vector3(targetLimit, 0.02, 0),
  ]
  const geometry = new THREE.BufferGeometry().setFromPoints(points)
  const targetPath = new THREE.Line(
    geometry,
    new THREE.LineDashedMaterial({
      color: sceneColors.targetPath,
      dashSize: 0.5,
      gapSize: 0.32,
      transparent: true,
      opacity: 0.65,
    }),
  )

  targetPath.computeLineDistances()
  scene.add(targetPath)

  return targetPath
}