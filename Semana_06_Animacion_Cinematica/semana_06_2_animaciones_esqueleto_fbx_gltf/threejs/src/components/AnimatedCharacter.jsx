import { useFrame } from '@react-three/fiber';
import { useEffect, useRef } from 'react';
import { useAnimations, useGLTF } from '@react-three/drei';
import * as THREE from 'three';

const MODEL_URL = '/models/BrainStem.gltf';

export default function AnimatedCharacter({
  activeClip,
  mode,
  replaySignal,
  onClips,
  onProgress,
  onHasAnimation,
  ...props
}) {
  const group = useRef();
  const { scene, animations } = useGLTF(MODEL_URL);
  const { actions, names } = useAnimations(animations, group);

  useEffect(() => {
    if (!group.current) return;

    scene.updateMatrixWorld(true);

    const box = new THREE.Box3().setFromObject(scene);
    const size = new THREE.Vector3();
    const center = new THREE.Vector3();

    box.getSize(size);
    box.getCenter(center);

    if (size.y === 0) return;

    const targetHeight = 1.7;
    const scale = targetHeight / size.y;

    group.current.scale.setScalar(scale);
    group.current.position.set(
      -center.x * scale,
      -box.min.y * scale,
      -center.z * scale
    );
  }, [scene]);

  useEffect(() => {
    scene.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
      if (child.isSkinnedMesh) {
        child.frustumCulled = false;
      }
    });
  }, [scene]);

  useEffect(() => {
    if (onClips) onClips(names);
  }, [names, onClips]);

  useEffect(() => {
    if (!onHasAnimation) return;
    onHasAnimation(Boolean(actions?.[activeClip]));
  }, [actions, activeClip, onHasAnimation]);

  useFrame(() => {
    if (!onProgress) return;

    const action = actions?.[activeClip];
    if (!action || !action.getClip) {
      onProgress(0);
      return;
    }

    const clip = action.getClip();
    const duration = clip?.duration ?? 0;

    if (!duration) {
      onProgress(0);
      return;
    }

    onProgress((action.time % duration) / duration);
  });

  useEffect(() => {
    if (!activeClip || !actions) return;

    Object.values(actions).forEach((action) => action.stop());

    const action = actions[activeClip];
    if (!action) return;

    if (mode === 'idle') {
      action.reset();
      action.play();
      action.paused = true;
      action.time = 0;
      return;
    }

    action.reset();
    action.fadeIn(0.2);
    action.play();
    action.paused = false;

    return () => {
      action.fadeOut(0.2);
    };
  }, [actions, activeClip, mode]);

  useEffect(() => {
    if (mode !== 'dance') return;
    const action = actions?.[activeClip];
    if (!action) return;
    action.reset().play();
  }, [actions, activeClip, mode, replaySignal]);

  return (
    <group ref={group} {...props} dispose={null}>
      <primitive object={scene} />
    </group>
  );
}

useGLTF.preload(MODEL_URL);
