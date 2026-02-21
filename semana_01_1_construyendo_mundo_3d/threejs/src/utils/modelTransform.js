import { Box3, Vector3 } from 'three'

const defaultTransform = {
  position: [0, 0, 0],
  scale: 1,
}

export function calculateModelTransform(loadedModel, targetSize) {
  if (!loadedModel) {
    return defaultTransform
  }

  const bounds = new Box3().setFromObject(loadedModel)
  const center = new Vector3()
  const size = new Vector3()

  bounds.getCenter(center)
  bounds.getSize(size)

  const sizeValues = [size.x, size.y, size.z].filter((value) => Number.isFinite(value) && value > 0)
  const maxAxisLength = sizeValues.length ? Math.max(...sizeValues) : 1
  const fitScale = targetSize / maxAxisLength

  if (!Number.isFinite(fitScale) || fitScale <= 0) {
    return defaultTransform
  }

  return {
    position: [
      Number.isFinite(center.x) ? -center.x * fitScale : 0,
      Number.isFinite(center.y) ? -center.y * fitScale : 0,
      Number.isFinite(center.z) ? -center.z * fitScale : 0,
    ],
    scale: fitScale,
  }
}