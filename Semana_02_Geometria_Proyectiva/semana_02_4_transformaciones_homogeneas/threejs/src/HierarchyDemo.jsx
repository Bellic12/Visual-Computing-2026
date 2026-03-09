import * as THREE from "three";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import { useMemo, useRef, useState } from "react";

export default function HierarchyDemo() {
  const baseRef = useRef();
  const armRef = useRef();
  const endRef = useRef();

  const tmp = useMemo(() => new THREE.Vector3(), []);
  const [info, setInfo] = useState({ endLocal: "—", endWorld: "—" });

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    // Base (padre): movimiento + rotación
    if (baseRef.current) {
      baseRef.current.rotation.y = t * 0.6;
      baseRef.current.position.x = Math.sin(t) * 1.2;
    }

    // Arm (hijo): rotación local limitada a 180° (±90°)
    if (armRef.current) {
      const angle = Math.sin(t * 1.2) * (Math.PI / 2);
      armRef.current.rotation.z = angle;
    }

    // EndEffector: local vs world
    if (endRef.current) {
      const local = endRef.current.position; // local al padre
      endRef.current.getWorldPosition(tmp); // world

      // actualiza ~3 veces por segundo aprox
      if (Math.floor(t * 10) % 3 === 0) {
        setInfo({
          endLocal: `(${local.x.toFixed(2)}, ${local.y.toFixed(2)}, ${local.z.toFixed(2)})`,
          endWorld: `(${tmp.x.toFixed(2)}, ${tmp.y.toFixed(2)}, ${tmp.z.toFixed(2)})`,
        });
      }
    }
  });

  return (
    <>
      {/* Base */}
      <group ref={baseRef}>
        <mesh>
          <boxGeometry args={[2, 0.3, 2]} />
          <meshStandardMaterial color="#999" />
        </mesh>

        {/* ArmPivot */}
        <group ref={armRef} position={[0, 0.15, 0]}>
          {/* ArmMesh */}
          <mesh position={[0, 0.6, 0]}>
            <boxGeometry args={[0.3, 1.2, 0.3]} />
            <meshStandardMaterial color="#bbb" />
          </mesh>

          {/* EndEffector */}
          <mesh ref={endRef} position={[0, 1.2, 0]}>
            <sphereGeometry args={[0.15, 24, 24]} />
            <meshStandardMaterial color="#fff" />
          </mesh>
        </group>
      </group>

      {/* Overlay DOM (sin <b> para evitar error R3F) */}
      <Html fullscreen>
        <div
          style={{
            position: "absolute",
            top: 12,
            left: 12,
            padding: "10px 12px",
            background: "rgba(0,0,0,0.55)",
            color: "white",
            fontFamily: "monospace",
            fontSize: 13,
            borderRadius: 8,
            lineHeight: 1.4,
            pointerEvents: "none",
          }}
        >
          <div style={{ fontWeight: 700 }}>EndEffector</div>
          <div>local: {info.endLocal}</div>
          <div>world: {info.endWorld}</div>
        </div>
      </Html>
    </>
  );
}