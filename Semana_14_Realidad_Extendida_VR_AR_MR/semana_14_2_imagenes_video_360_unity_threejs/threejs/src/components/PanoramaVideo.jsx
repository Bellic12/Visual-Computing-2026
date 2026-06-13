import { useEffect, useState } from 'react'
import * as THREE from 'three'

export default function PanoramaVideo({ videoRef }) {
  const [texture, setTexture] = useState(null)

  useEffect(() => {
    const video = document.createElement('video')
    video.src = '/video360.mp4'
    video.loop = true
    video.muted = true
    video.playsInline = true
    video.crossOrigin = 'anonymous'
    video.play()
    videoRef.current = video

    const tex = new THREE.VideoTexture(video)
    setTexture(tex)

    return () => {
      video.pause()
      video.src = ''
      video.load()
      tex.dispose()
      videoRef.current = null
    }
  }, [videoRef])

  if (!texture) return null

  return (
    <mesh scale={[-1, 1, 1]}>
      <sphereGeometry args={[10, 60, 40]} />
      <meshBasicMaterial map={texture} side={THREE.BackSide} />
    </mesh>
  )
}
