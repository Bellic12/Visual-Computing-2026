import { useMemo } from 'react';
import * as THREE from 'three';
import { PROJECTION_TARGET } from '../constants/cameraConfig';
import { DEPTH_GUIDES, DEPTH_OBJECTS } from '../constants/sceneConfig';

function GeometryByType({ type }) {
  if (type === 'sphere') {
    return <sphereGeometry args={[0.6, 48, 48]} />;
  }
  if (type === 'torus') {
    return <torusGeometry args={[0.7, 0.2, 24, 64]} />;
  }
  if (type === 'capsule') {
    return <capsuleGeometry args={[0.4, 0.8, 8, 16]} />;
  }
  return <boxGeometry args={[1, 1, 1]} />;
}

function DepthObject({ item }) {
  return (
    <mesh castShadow receiveShadow position={item.position} scale={item.scale}>
      <GeometryByType type={item.type} />
      <meshStandardMaterial color={item.color} roughness={0.35} metalness={0.1} />
    </mesh>
  );
}

export function SceneObjects() {
  const gridHelper = useMemo(
    () => new THREE.GridHelper(30, 30, '#6c757d', '#ced4da'),
    [],
  );
  const axesHelper = useMemo(() => new THREE.AxesHelper(4), []);

  return (
    <>
      <hemisphereLight intensity={0.5} groundColor="#b6c2cf" />
      <ambientLight intensity={0.55} />
      <directionalLight
        position={[8, 12, 4]}
        castShadow
        intensity={1}
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />

      <primitive object={gridHelper} position={[0, -1, 0]} />
      <primitive object={axesHelper} position={[0, 0, 0]} />

      <mesh receiveShadow rotation={[-Math.PI * 0.5, 0, 0]} position={[0, -1, -6]}>
        <planeGeometry args={[30, 30]} />
        <meshStandardMaterial color="#f8f9fa" roughness={0.95} />
      </mesh>

      {DEPTH_GUIDES.map((zValue) => (
        <mesh key={`guide-${zValue}`} position={[0, 1.1, zValue]}>
          <planeGeometry args={[18, 4.2]} />
          <meshBasicMaterial
            color="#495057"
            transparent
            opacity={0.06}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}

      {DEPTH_OBJECTS.map((item) => (
        <DepthObject key={item.id} item={item} />
      ))}

      <mesh position={PROJECTION_TARGET} castShadow>
        <sphereGeometry args={[0.22, 28, 28]} />
        <meshStandardMaterial color="#d00000" emissive="#7f1d1d" emissiveIntensity={0.8} />
      </mesh>
    </>
  );
}
