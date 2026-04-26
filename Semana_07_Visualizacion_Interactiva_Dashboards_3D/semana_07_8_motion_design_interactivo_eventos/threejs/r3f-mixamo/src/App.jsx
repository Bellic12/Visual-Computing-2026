import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import Scene from "./Scene";

export default function App() {
  return (
    <Canvas
      camera={{ position: [0, 1.5, 3] }}
      style={{ height: "100vh" }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[2, 2, 2]} />
      <Scene />
      <OrbitControls />
    </Canvas>
  );
}