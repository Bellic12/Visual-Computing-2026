import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import RobotArm from "./RobotArm";

export default function App() {
  return (
    <Canvas camera={{ position: [5, 5, 5] }} style={{ width: "100vw", height: "100vh" }}>
      <ambientLight />
      <pointLight position={[10, 10, 10]} />
      <RobotArm />
      <OrbitControls />
    </Canvas>
  );
}