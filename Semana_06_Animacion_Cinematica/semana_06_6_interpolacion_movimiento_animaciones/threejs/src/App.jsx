import React, { useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";

function Scene() {
  const boxRef = useRef();
  const sphRef = useRef();
  const [t, setT] = useState(0);

  const start = new THREE.Vector3(-3, 0, 0);
  const end = new THREE.Vector3(3, 0, 0);

  const vel = useRef(0.2);

  const qStart = useRef(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, 0)));
  const qEnd = useRef(new THREE.Quaternion().setFromEuler(new THREE.Euler(0, 0, -Math.PI)));
  const qCurrent = useRef(new THREE.Quaternion());

  const control = new THREE.Vector3(0, 2, 0);

  const curve = useMemo(() => {
    return new THREE.QuadraticBezierCurve3(start, control, end);
  }, []);

  const points = useMemo(() => curve.getPoints(50), [curve]);

  const curveGeometry = useMemo(() => {
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [points]);

  useFrame((_, delta) => {
    setT((prev) => {
      let next = prev + delta * vel.current; 

      if (next > 1) {
        next = 1;
        vel.current *= -1;
      } else if (next < 0) {
        next = 0;
        vel.current *= -1;
      }

      // Interpolación lineal
      const x = THREE.MathUtils.lerp(start.x, end.x, next);
      const y = THREE.MathUtils.lerp(start.y, end.y, next);
      const z = THREE.MathUtils.lerp(start.z, end.z, next);

      const point = curve.getPoint(next);

      qCurrent.current.slerpQuaternions(qStart.current, qEnd.current, next) 

      if (boxRef.current) {
        sphRef.current.position.set(x, y, z);
        boxRef.current.position.copy(point);
        boxRef.current.quaternion.copy(qCurrent.current);
      }

      return next;
    });
  });

  return (
    <>
      {/* Fondo oscuro */}
      <color attach="background" args={["#2b2b2b"]} />

      {/* Controles de cámara */}
      <OrbitControls />

      {/* Esfera */}
      <mesh ref={sphRef} position={[-3, 0, 0]}>
        <icosahedronGeometry args={[0.3, 2]}/>
        <meshStandardMaterial color="orange"/>
      </mesh>

      {/* Cubo */}
      <mesh ref={boxRef} position={[-3, 0, 0]}>
        <boxGeometry args={[0.5, 0.5, 0.5]} />
        <meshStandardMaterial color="orange" />
      </mesh>

      {/* Punto inicio */}
      <mesh position={start}>
        <sphereGeometry args={[0.05, 16, 16]} />
        <meshStandardMaterial color="blue" />
      </mesh>

      {/* Punto fin */}
      <mesh position={end}>
        <sphereGeometry args={[0.05, 16, 16]} />
        <meshStandardMaterial color="blue" />
      </mesh>

      {/* Punto de control */}
      <mesh position={control}>
        <sphereGeometry args={[0.05, 16, 16]} />
        <meshStandardMaterial color="red" />
      </mesh>

      {/* Bezier */}
      <line geometry={curveGeometry}>
        <lineBasicMaterial color="white" />
      </line>

      {/* Luces */}
      <ambientLight intensity={0.5} />
      <pointLight position={[5, 5, 5]} />
    </>
  );
}

export default function App() {
  return (
    <Canvas camera={{ position: [0, 2, 6], fov: 60 }}
            style={{ width: "98.7vw", height: "98.7vh" }}>
      <Scene />
    </Canvas>
  );
}
