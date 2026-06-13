import { useTexture } from '@react-three/drei'
import * as THREE from 'three'

export default function PanoramaImage() {
  const texture = useTexture('/panorama.jpg')

  return (
    <mesh scale={[-1, 1, 1]}>
      <sphereGeometry args={[10, 60, 40]} />
      <meshBasicMaterial map={texture} side={THREE.BackSide} />
    </mesh>
  )
}
