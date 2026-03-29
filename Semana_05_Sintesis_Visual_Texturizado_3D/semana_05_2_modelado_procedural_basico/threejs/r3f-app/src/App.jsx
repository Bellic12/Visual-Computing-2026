import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";

/* ================= GRID ================= */
function Grid() {
  const size = 8;
  const spacing = 5;

  const positions = useMemo(() => {
    let arr = [];
    for (let x = -size; x <= size; x++) {
      for (let z = -size; z <= size; z++) {
        arr.push([x * spacing, 0, z * spacing]);
      }
    }
    return arr;
  }, []);

  return (
    <>
      {positions.map((pos, i) => (
        <mesh key={i} position={pos}>
          <boxGeometry args={[1,1,1]} />
          <meshStandardMaterial color="orange" />
        </mesh>
      ))}
    </>
  );
}

/* ================= ESPIRAL ================= */
function Spiral() {
  const items = useMemo(() => {
    return Array.from({ length: 60 }, (_, i) => {
      const angle = i * 0.3;
      const radius = 0.15 * i;
      return [
        Math.cos(angle) * radius,
        i * 0.1,
        Math.sin(angle) * radius,
      ];
    });
  }, []);

  return (
    <>
      {items.map((pos, i) => (
        <mesh key={i} position={pos}>
          <sphereGeometry args={[0.25, 16, 16]} />
          <meshStandardMaterial color="hotpink" />
        </mesh>
      ))}
    </>
  );
}

/* ================= GEOMETRÍA DINÁMICA ================= */
function DeformingSphere() {
  const ref = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const geom = ref.current.geometry;
    const pos = geom.attributes.position;

    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      const z = pos.getZ(i);

      const wave = Math.sin(t + x * 2 + y * 2);

      pos.setXYZ(
        i,
        x + wave * 0.05,
        y + wave * 0.05,
        z + wave * 0.05
      );
    }

    pos.needsUpdate = true;
    geom.computeVertexNormals();
  });

  return (
    <mesh ref={ref} position={[0, 2, 0]}>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="cyan" wireframe />
    </mesh>
  );
}

/* ================= FRACTAL ================= */
function Fractal({ depth = 0, maxDepth = 4 }) {
  if (depth > maxDepth) return null;

  return (
    <group>
      {/* tronco */}
      <mesh position={[0, 0.5, 0]}>
        <cylinderGeometry args={[0.05, 0.05, 1]} />
        <meshStandardMaterial color="green" />
      </mesh>

      {/* ramas */}
      <group position={[0, 1, 0]}>
        <group rotation={[0, 0, 0.5]}>
          <Fractal depth={depth + 1} maxDepth={maxDepth} />
        </group>
        <group rotation={[0, 0, -0.5]}>
          <Fractal depth={depth + 1} maxDepth={maxDepth} />
        </group>
      </group>
    </group>
  );
}

/* ================= ESCENA ================= */
export default function App() {
  return (
    <Canvas style={{ width: "100vw", height: "100vh" }} camera={{ position: [6,6,10]}}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />

      {/* Elementos del taller */}
      <Grid />
      <Spiral />
      <DeformingSphere />

      <group position={[0, 0, -6]}>
        <Fractal />
      </group>
    </Canvas>
  );
}