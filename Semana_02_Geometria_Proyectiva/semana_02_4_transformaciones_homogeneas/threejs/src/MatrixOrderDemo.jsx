import * as THREE from "three";
import { useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import { useMemo, useRef, useState } from "react";

export default function MatrixOrderDemo() {
  const markerTR = useRef();
  const markerRT = useRef();

  const [text, setText] = useState({ tr: "—", rt: "—", eq: "—" });

  const p = useMemo(() => new THREE.Vector4(1, 0, 0, 1), []);
  const tmpTR = useMemo(() => new THREE.Vector4(), []);
  const tmpRT = useMemo(() => new THREE.Vector4(), []);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    // Parámetros (puedes jugar con estos)
    const translation = new THREE.Vector3(2, 0, 0);
    const angle = (Math.PI / 4) + t * 0.5; // rota + anima

    const T = new THREE.Matrix4().makeTranslation(
      translation.x,
      translation.y,
      translation.z
    );
    const R = new THREE.Matrix4().makeRotationY(angle);

    // (T*R)*p
    const M_TR = new THREE.Matrix4().multiplyMatrices(T, R);
    tmpTR.copy(p).applyMatrix4(M_TR);

    // (R*T)*p
    const M_RT = new THREE.Matrix4().multiplyMatrices(R, T);
    tmpRT.copy(p).applyMatrix4(M_RT);

    if (markerTR.current) markerTR.current.position.set(tmpTR.x, tmpTR.y, tmpTR.z);
    if (markerRT.current) markerRT.current.position.set(tmpRT.x, tmpRT.y, tmpRT.z);

    if (Math.floor(t * 10) % 3 === 0) {
      const eq =
        Math.abs(tmpTR.x - tmpRT.x) < 1e-4 &&
        Math.abs(tmpTR.y - tmpRT.y) < 1e-4 &&
        Math.abs(tmpTR.z - tmpRT.z) < 1e-4;

      setText({
        tr: `(${tmpTR.x.toFixed(2)}, ${tmpTR.y.toFixed(2)}, ${tmpTR.z.toFixed(2)})`,
        rt: `(${tmpRT.x.toFixed(2)}, ${tmpRT.y.toFixed(2)}, ${tmpRT.z.toFixed(2)})`,
        eq: eq ? "true" : "false",
      });
    }
  });

  return (
    <>
      {/* Punto TR */}
      <mesh ref={markerTR}>
        <sphereGeometry args={[0.12, 24, 24]} />
        <meshStandardMaterial color="#ff4d4d" />
      </mesh>

      {/* Punto RT */}
      <mesh ref={markerRT}>
        <sphereGeometry args={[0.12, 24, 24]} />
        <meshStandardMaterial color="#4d79ff" />
      </mesh>

      <Html fullscreen>
        <div
          style={{
            position: "absolute",
            top: 12,
            right: 12,
            padding: "10px 12px",
            background: "rgba(0,0,0,0.55)",
            color: "white",
            fontFamily: "monospace",
            fontSize: 13,
            borderRadius: 8,
            lineHeight: 1.4,
            pointerEvents: "none",
            maxWidth: 380,
          }}
        >
          <div style={{ fontWeight: 700 }}>Matrix Order (non-commutative)</div>
          <div>(T*R)*p: {text.tr}</div>
          <div>(R*T)*p: {text.rt}</div>
          <div>Equal?: {text.eq}</div>
          <div style={{ opacity: 0.85, marginTop: 6 }}>
            p = (1,0,0,1), T = translate(2,0,0), R = rotateY(angle)
          </div>
        </div>
      </Html>
    </>
  );
}