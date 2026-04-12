import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';

export default function DanceMarker({ active, hasAnimation, progressRef }) {
  const ref = useRef();

  useFrame((state, delta) => {
    if (!ref.current) return;

    if (!active) {
      ref.current.rotation.y = 0;
      ref.current.position.set(1.4, 0.2, 0);
      const material = ref.current.material;
      const target = Array.isArray(material) ? material[0] : material;
      if (target) target.emissiveIntensity = 0.08;
      return;
    }

    const progress = progressRef?.current ?? 0;
    const phase = hasAnimation
      ? progress
      : (state.clock.elapsedTime * 0.1) % 1;
    const angle = phase * Math.PI * 2;

    ref.current.rotation.y = angle;
    ref.current.position.x = Math.cos(angle) * 1.4;
    ref.current.position.z = Math.sin(angle) * 1.4;
    ref.current.position.y = 0.2 + Math.sin(angle * 2) * 0.1;

    const material = ref.current.material;
    const target = Array.isArray(material) ? material[0] : material;
    if (target) target.emissiveIntensity = 0.2 + phase * 0.6;
  });

  return (
    <mesh ref={ref} position={[1.4, 0.2, 0]} castShadow>
      <sphereGeometry args={[0.12, 32, 32]} />
      <meshStandardMaterial
        color="#ff7a59"
        emissive="#ff9b7c"
        emissiveIntensity={0.4}
      />
    </mesh>
  );
}
