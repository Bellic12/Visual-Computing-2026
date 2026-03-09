import * as THREE from 'three'
import { SCENE_POINTS, PROJECTION_WIDTH } from './constants'

function degToRad(value) {
  return (value * Math.PI) / 180
}

export function computeProjectionData(cameraState, distortionState) {
  const imageWidth = PROJECTION_WIDTH
  const imageHeight = Math.round(imageWidth / cameraState.aspect)

  const camera = new THREE.PerspectiveCamera(
    cameraState.fov,
    cameraState.aspect,
    cameraState.near,
    cameraState.far
  )

  camera.position.set(cameraState.x, cameraState.y, cameraState.z)
  camera.rotation.order = 'YXZ'
  camera.rotation.set(degToRad(cameraState.pitch), degToRad(cameraState.yaw), 0)
  camera.updateMatrixWorld(true)

  const fy = (imageHeight * 0.5) / Math.tan(degToRad(cameraState.fov) * 0.5)
  const fx = fy
  const cx = imageWidth * 0.5
  const cy = imageHeight * 0.5

  let distortionErrorAccumulator = 0
  let visibleCount = 0

  const points = SCENE_POINTS.map((point) => {
    const world = new THREE.Vector3(...point.position)
    const cameraSpace = world.clone().applyMatrix4(camera.matrixWorldInverse)
    const depth = -cameraSpace.z

    if (depth <= 0) {
      return {
        ...point,
        isInFront: false,
        undistorted: { u: 0, v: 0 },
        distorted: { u: 0, v: 0 },
        cameraSpace: { x: cameraSpace.x, y: cameraSpace.y, z: cameraSpace.z },
        depth,
        r2: 0,
        radialFactor: 0
      }
    }

    const xn = cameraSpace.x / depth
    const yn = cameraSpace.y / depth

    const u = fx * xn + cx
    const v = cy - fy * yn

    const r2 = xn * xn + yn * yn
    const radialFactor =
      1 + distortionState.k1 * r2 + distortionState.k2 * r2 * r2

    const xd = distortionState.enabled ? xn * radialFactor : xn
    const yd = distortionState.enabled ? yn * radialFactor : yn

    const ud = fx * xd + cx
    const vd = cy - fy * yd

    const distortionDelta = Math.hypot(ud - u, vd - v)
    const inFrame =
      u >= 0 &&
      u <= imageWidth &&
      v >= 0 &&
      v <= imageHeight &&
      depth >= cameraState.near &&
      depth <= cameraState.far

    if (inFrame) {
      visibleCount += 1
      distortionErrorAccumulator += distortionDelta
    }

    return {
      ...point,
      isInFront: true,
      inFrame,
      undistorted: { u, v },
      distorted: { u: ud, v: vd },
      cameraSpace: { x: cameraSpace.x, y: cameraSpace.y, z: cameraSpace.z },
      depth,
      r2,
      radialFactor
    }
  })

  const meanDistortion =
    visibleCount > 0 ? distortionErrorAccumulator / visibleCount : 0

  return {
    imageWidth,
    imageHeight,
    intrinsics: { fx, fy, cx, cy },
    points,
    meanDistortion,
    visibleCount
  }
}
