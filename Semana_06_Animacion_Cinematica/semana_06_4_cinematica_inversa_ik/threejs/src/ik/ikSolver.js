import * as THREE from 'three'

export function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function shortestAngleDelta(currentAngle, targetAngle) {
  let delta = targetAngle - currentAngle

  while (delta > Math.PI) {
    delta -= Math.PI * 2
  }

  while (delta < -Math.PI) {
    delta += Math.PI * 2
  }

  return delta
}

export function solveCcd({
  root,
  joints,
  endEffector,
  targetPosition,
  iterations = 6,
  influence = 0.85,
  threshold = 0.08,
  maxStep = 0.09,
}) {
  const jointWorldPosition = new THREE.Vector3()
  const endWorldPosition = new THREE.Vector3()

  let distance = Infinity

  for (let iteration = 0; iteration < iterations; iteration += 1) {
    root.updateMatrixWorld(true)
    endEffector.getWorldPosition(endWorldPosition)
    distance = endWorldPosition.distanceTo(targetPosition)

    if (distance <= threshold) {
      break
    }

    for (let jointIndex = joints.length - 1; jointIndex >= 0; jointIndex -= 1) {
      const joint = joints[jointIndex]

      joint.getWorldPosition(jointWorldPosition)
      endEffector.getWorldPosition(endWorldPosition)

      const toEndX = endWorldPosition.x - jointWorldPosition.x
      const toEndZ = endWorldPosition.z - jointWorldPosition.z
      const toTargetX = targetPosition.x - jointWorldPosition.x
      const toTargetZ = targetPosition.z - jointWorldPosition.z

      const endLength = Math.hypot(toEndX, toEndZ)
      const targetLength = Math.hypot(toTargetX, toTargetZ)

      if (endLength < 1e-5 || targetLength < 1e-5) {
        continue
      }

      const currentAngle = Math.atan2(toEndZ, toEndX)
      const targetAngle = Math.atan2(toTargetZ, toTargetX)
      const step = shortestAngleDelta(currentAngle, targetAngle) * influence
      const limitedStep = clamp(step, -maxStep, maxStep)

      joint.rotation.y -= limitedStep
      root.updateMatrixWorld(true)
    }
  }

  root.updateMatrixWorld(true)
  endEffector.getWorldPosition(endWorldPosition)

  return {
    distance: endWorldPosition.distanceTo(targetPosition),
    solved: endWorldPosition.distanceTo(targetPosition) <= threshold,
  }
}