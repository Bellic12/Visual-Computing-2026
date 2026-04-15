import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

export default function RobotArm() {
  const base = useRef();
  const joint1 = useRef();
  const joint2 = useRef();

  useFrame(({ clock }) => {
    const t = clock.elapsedTime;

    if (base.current && joint1.current && joint2.current) {
      base.current.rotation.y = Math.sin(t) * 0.5;
      joint1.current.rotation.z = Math.sin(t * 1.5) * 0.5;
      joint2.current.rotation.z = Math.sin(t * 2) * 0.5;
    }
  });

  return (
    <group ref={base}>
      {/* BASE */}
      <mesh position={[0, 0.5, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="red" />
      </mesh>

      {/* BRAZO 1 */}
      <group ref={joint1} position={[0, 1, 0]}>
        <mesh position={[0, 1, 0]}>
          <boxGeometry args={[0.5, 2, 0.5]} />
          <meshStandardMaterial color="green" />
        </mesh>

        {/* BRAZO 2 */}
        <group ref={joint2} position={[0, 2, 0]}>
          <mesh position={[0, 1, 0]}>
            <boxGeometry args={[0.4, 2, 0.4]} />
            <meshStandardMaterial color="blue" />
          </mesh>
        </group>
      </group>
    </group>
  );
}