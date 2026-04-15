export const segmentLengths = [3.2, 2.7, 2.25, 1.8]
export const targetHeight = 0.34
export const targetLimitFactor = 0.86

export const sceneDefaults = {
  iterations: 2,
  influence: 0.35,
  autoTarget: false,
}

export const sceneColors = {
  background: 0x050913,
  fog: 0x050913,
  ambient: 0xbfd7ff,
  keyLight: 0xffffff,
  rimLight: 0x72d7ff,
  gridMajor: 0x88a4c7,
  gridMinor: 0x1c2b45,
  floor: 0x09111c,
  root: 0xffc857,
  rootEmissive: 0x7a5200,
  segmentBase: 0x1a2d45,
  target: 0x59d6ff,
  targetEmissive: 0x0d7aa6,
  targetRing: 0x88f0ff,
  targetRingEmissive: 0x145c74,
  guide: 0x88f0ff,
  targetPath: 0x274266,
}

export const segmentCount = segmentLengths.length
export const totalReach = segmentLengths.reduce((sum, length) => sum + length, 0)
export const targetLimit = totalReach * targetLimitFactor