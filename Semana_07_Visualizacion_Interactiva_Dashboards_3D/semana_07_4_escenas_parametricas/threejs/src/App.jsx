import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import SceneObjects from "./SceneObjects";

export default function App() {
  return (
    <Canvas style={{ width: "99vw", height: "98vh" }}>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />

      <SceneObjects />

      <OrbitControls />
    </Canvas>
  );
}