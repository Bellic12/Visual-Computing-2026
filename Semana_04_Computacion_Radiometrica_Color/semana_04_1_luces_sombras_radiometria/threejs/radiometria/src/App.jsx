import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useControls } from "leva";

function Lights() {
  const { intensity, color, posX, posY, posZ } = useControls({
    intensity: { value: 2, min: 0, max: 5 },
    color: "#ffffff",
    posX: { value: 2, min: -10, max: 10 },
    posY: { value: 5, min: 0, max: 10 },
    posZ: { value: 2, min: -10, max: 10 },
  });

  return (
    <>
      {/* Luz ambiental */}
      <ambientLight intensity={0.3} />

      {/* Luz direccional */}
      <directionalLight
        position={[5, 10, 5]}
        intensity={1}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />

      {/* Luz puntual interactiva */}
      <pointLight
        position={[posX, posY, posZ]}
        intensity={intensity}
        color={color}
        castShadow
      />
    </>
  );
}

export default function App() {
  return (
    <Canvas
      shadows
      camera={{ position: [5, 5, 5] }}
      style={{ width: "100vw", height: "100vh" }}
    >
      {/* Fondo */}
      <color attach="background" args={["#111"]} />

      {/* Luces */}
      <Lights />

      {/* Plano */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="gray" />
      </mesh>

      {/* Cubo */}
      <mesh position={[0, 1, 0]} castShadow>
        <boxGeometry />
        <meshStandardMaterial
          color="orange"
          metalness={0.3}
          roughness={0.4}
        />
      </mesh>

      {/* Esfera */}
      <mesh position={[2, 1, 0]} castShadow>
        <sphereGeometry />
        <meshStandardMaterial
          color="skyblue"
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* Torus */}
      <mesh position={[-2, 1, 0]} castShadow>
        <torusKnotGeometry />
        <meshPhysicalMaterial
          color="hotpink"
          metalness={1}
          roughness={0.2}
          clearcoat={1}
        />
      </mesh>

      {/* Controles */}
      <OrbitControls />
    </Canvas>
  );
}