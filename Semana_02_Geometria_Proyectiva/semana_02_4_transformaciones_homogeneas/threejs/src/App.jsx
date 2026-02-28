import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import MatrixOrderDemo from "./MatrixOrderDemo";

export default function App() {
  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <Canvas camera={{ position: [5, 3, 6], fov: 50 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 10, 5]} intensity={1} />
        <gridHelper args={[20, 20]} />
        <axesHelper args={[2]} />
        <OrbitControls />
        <MatrixOrderDemo />
      </Canvas>
    </div>
  );
}