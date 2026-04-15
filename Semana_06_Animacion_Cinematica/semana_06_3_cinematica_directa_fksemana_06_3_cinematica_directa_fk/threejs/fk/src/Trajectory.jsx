import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

export default function Trajectory({ target }) {
  const points = useRef([]);

  useFrame(() => {
    if (!target.current) return;

    const pos = target.current.getWorldPosition(new THREE.Vector3());
    points.current.push(pos.clone());

    if (points.current.length > 100) {
      points.current.shift();
    }
  });

  return (
    <line>
      <bufferGeometry
        setFromPoints={points.current}
      />
      <lineBasicMaterial color="yellow" />
    </line>
  );
}