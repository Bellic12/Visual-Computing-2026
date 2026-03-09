export const CAMERA_MODE = {
  PERSPECTIVE: 'perspective',
  ORTHOGRAPHIC: 'orthographic',
};

export const CAMERA_CLIP_PLANES = {
  near: 0.1,
  far: 80,
};

export const DEFAULT_PERSPECTIVE = {
  fov: 58,
  position: [9, 6, 12],
};

export const DEFAULT_ORTHOGRAPHIC = {
  size: 5.5,
  position: [9, 6, 12],
};

export const FOV_RANGE = {
  min: 25,
  max: 110,
  step: 1,
};

export const ORTHO_SIZE_RANGE = {
  min: 2,
  max: 14,
  step: 0.1,
};

export const PROJECTION_TARGET = [1.5, 1.2, -8];
