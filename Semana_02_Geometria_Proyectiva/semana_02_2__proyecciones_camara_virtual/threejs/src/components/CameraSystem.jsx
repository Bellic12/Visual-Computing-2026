import {
  OrthographicCamera,
  OrbitControls,
  PerspectiveCamera,
} from '@react-three/drei';
import { useFrame, useThree } from '@react-three/fiber';
import { useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import {
  CAMERA_CLIP_PLANES,
  CAMERA_MODE,
  DEFAULT_ORTHOGRAPHIC,
  DEFAULT_PERSPECTIVE,
  PROJECTION_TARGET,
} from '../constants/cameraConfig';

const round = (value, precision = 3) => Number(value.toFixed(precision));

const getOrthoBounds = (aspect, size) => {
  const halfHeight = size;
  const halfWidth = halfHeight * aspect;
  return {
    left: -halfWidth,
    right: halfWidth,
    top: halfHeight,
    bottom: -halfHeight,
  };
};

export function CameraSystem({
  mode,
  fov,
  orthoSize,
  resetToken,
  onTelemetry,
  onProjection,
}) {
  const perspectiveRef = useRef(null);
  const orthographicRef = useRef(null);
  const controlsRef = useRef(null);
  const lastTelemetryKeyRef = useRef('');
  const lastProjectionKeyRef = useRef('');

  const projectionPointRef = useRef(new THREE.Vector3());
  const { size } = useThree();
  const aspect = size.width / size.height || 1;

  const orbitTarget = useMemo(() => new THREE.Vector3(0, 1, -6), []);
  const targetPoint = useMemo(() => new THREE.Vector3(...PROJECTION_TARGET), []);

  useEffect(() => {
    const perspective = perspectiveRef.current;
    if (!perspective) {
      return;
    }

    perspective.fov = fov;
    perspective.aspect = aspect;
    perspective.near = CAMERA_CLIP_PLANES.near;
    perspective.far = CAMERA_CLIP_PLANES.far;
    perspective.updateProjectionMatrix();
  }, [aspect, fov]);

  useEffect(() => {
    const orthographic = orthographicRef.current;
    if (!orthographic) {
      return;
    }

    const bounds = getOrthoBounds(aspect, orthoSize);
    orthographic.left = bounds.left;
    orthographic.right = bounds.right;
    orthographic.top = bounds.top;
    orthographic.bottom = bounds.bottom;
    orthographic.near = CAMERA_CLIP_PLANES.near;
    orthographic.far = CAMERA_CLIP_PLANES.far;
    orthographic.updateProjectionMatrix();
  }, [aspect, orthoSize]);

  useEffect(() => {
    const perspective = perspectiveRef.current;
    const orthographic = orthographicRef.current;
    const controls = controlsRef.current;

    if (!perspective || !orthographic || !controls) {
      return;
    }

    perspective.position.fromArray(DEFAULT_PERSPECTIVE.position);
    orthographic.position.fromArray(DEFAULT_ORTHOGRAPHIC.position);
    perspective.lookAt(orbitTarget);
    orthographic.lookAt(orbitTarget);

    controls.target.copy(orbitTarget);
    controls.update();
  }, [orbitTarget, resetToken]);

  useFrame(() => {
    const perspective = perspectiveRef.current;
    const orthographic = orthographicRef.current;
    const controls = controlsRef.current;

    if (!perspective || !orthographic || !controls) {
      return;
    }

    const activeCamera =
      mode === CAMERA_MODE.PERSPECTIVE ? perspective : orthographic;
    const passiveCamera =
      mode === CAMERA_MODE.PERSPECTIVE ? orthographic : perspective;

    passiveCamera.position.copy(activeCamera.position);
    passiveCamera.quaternion.copy(activeCamera.quaternion);
    passiveCamera.updateMatrixWorld();

    const bounds = getOrthoBounds(aspect, orthoSize);
    const cameraTelemetry = {
      mode,
      aspect: round(aspect),
      near: round(activeCamera.near, 2),
      far: round(activeCamera.far, 2),
      fov: round(perspective.fov, 2),
      left: round(bounds.left, 2),
      right: round(bounds.right, 2),
      top: round(bounds.top, 2),
      bottom: round(bounds.bottom, 2),
      position: [
        round(activeCamera.position.x, 2),
        round(activeCamera.position.y, 2),
        round(activeCamera.position.z, 2),
      ],
      target: [
        round(controls.target.x, 2),
        round(controls.target.y, 2),
        round(controls.target.z, 2),
      ],
    };

    if (onTelemetry) {
      const telemetryKey = JSON.stringify(cameraTelemetry);
      if (telemetryKey !== lastTelemetryKeyRef.current) {
        lastTelemetryKeyRef.current = telemetryKey;
        onTelemetry(cameraTelemetry);
      }
    }

    projectionPointRef.current.copy(targetPoint).project(activeCamera);

    const ndc = projectionPointRef.current;
    const projectionTelemetry = {
      world: [
        round(targetPoint.x, 2),
        round(targetPoint.y, 2),
        round(targetPoint.z, 2),
      ],
      ndc: [round(ndc.x, 3), round(ndc.y, 3), round(ndc.z, 3)],
      screen: [
        round(((ndc.x + 1) * 0.5) * size.width, 1),
        round(((1 - ndc.y) * 0.5) * size.height, 1),
      ],
      visible:
        Math.abs(ndc.x) <= 1 &&
        Math.abs(ndc.y) <= 1 &&
        ndc.z >= -1 &&
        ndc.z <= 1,
    };

    if (onProjection) {
      const projectionKey = JSON.stringify(projectionTelemetry);
      if (projectionKey !== lastProjectionKeyRef.current) {
        lastProjectionKeyRef.current = projectionKey;
        onProjection(projectionTelemetry);
      }
    }
  });

  return (
    <>
      <PerspectiveCamera
        ref={perspectiveRef}
        makeDefault={mode === CAMERA_MODE.PERSPECTIVE}
        position={DEFAULT_PERSPECTIVE.position}
      />
      <OrthographicCamera
        ref={orthographicRef}
        makeDefault={mode === CAMERA_MODE.ORTHOGRAPHIC}
        position={DEFAULT_ORTHOGRAPHIC.position}
      />
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.08}
        target={[0, 1, -6]}
        minDistance={3}
        maxDistance={28}
      />
    </>
  );
}
