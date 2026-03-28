import React, { useEffect, useRef, useState } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import { Grid } from '@react-three/drei';
import * as THREE from 'three';
import GUI from 'lil-gui';
import { TextureLoader } from 'three';

const PBRMaterialScene = () => {
  const { scene } = useThree();
  const guiRef = useRef(null);
  const spherePBRRef = useRef(null);
  const cubeRef = useRef(null);
  const cylinderRef = useRef(null);
  const texturesRef = useRef({});
  const materialsRef = useRef({});

  // Estados para propiedades de material
  const [materialProps, setMaterialProps] = useState({
    roughness: 0.3,
    metalness: 0.2,
    lightIntensity: 3.5,
  });

  // Cargar texturas desde archivos
  useEffect(() => {
    const textureLoader = new TextureLoader();

    // Función para cargar texturas PBR desde archivos PNG
    const loadTextureSet = (basePath) => {
      const textures = {};
      
      try {
        textures.color = textureLoader.load(`/textures/${basePath}/color.png`);
        textures.roughness = textureLoader.load(`/textures/${basePath}/roughness.png`);
        textures.normal = textureLoader.load(`/textures/${basePath}/normal.png`);
        
        // Algunas texturas pueden no tener metalness
        try {
          textures.metalness = textureLoader.load(`/textures/${basePath}/metalness.png`);
        } catch {
          textures.metalness = null;
        }
      } catch (error) {
        console.error(`Error loading textures from ${basePath}:`, error);
      }

      // Configurar filtros y propiedades de texturas
      Object.keys(textures).forEach(key => {
        const texture = textures[key];
        if (texture) {
          // Repetir texturas para mejor detalle
          texture.repeat.set(4, 4);
          texture.wrapS = THREE.RepeatWrapping;
          texture.wrapT = THREE.RepeatWrapping;
          
          // Configurar filtros
          texture.magFilter = THREE.LinearFilter;
          texture.minFilter = THREE.LinearMipMapLinearFilter;
          
          // Configurar color space según tipo de mapa
          if (key === 'normal') {
            // Normal maps no deben estar en sRGB
            texture.colorSpace = THREE.NoColorSpace;
          } else {
            // Los otros mapas sí necesitan sRGB
            texture.colorSpace = THREE.SRGBColorSpace;
          }
        }
      });

      return textures;
    };

    // Cargar tres sets de texturas diferentes
    texturesRef.current = {
      bricks: loadTextureSet('bricks'),
      metal034: loadTextureSet('metal034'),
      metal049: loadTextureSet('metal049'),
    };
  }, []);

  // Configurar escena con luces
  useEffect(() => {
    // Limpiar luces existentes
    scene.children = scene.children.filter(
      (child) => !(child instanceof THREE.Light)
    );

    // Luz ambiental
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    // Luz direccional
    const directionalLight = new THREE.DirectionalLight(0xffffff, materialProps.lightIntensity);
    directionalLight.position.set(10, 15, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.far = 50;
    scene.add(directionalLight);

    // Luz de relleno
    const fillLight = new THREE.DirectionalLight(0x4488ff, 0.5);
    fillLight.position.set(-10, 5, -10);
    scene.add(fillLight);
  }, [materialProps.lightIntensity, scene]);

  // Crear materiales y objetos
  useEffect(() => {
    if (!texturesRef.current.bricks || !texturesRef.current.metal034 || !texturesRef.current.metal049) {
      return; // Esperar a que las texturas carguen
    }

    // Material PBR para la esfera (Bricks)
    const bricksMaterial = new THREE.MeshStandardMaterial({
      map: texturesRef.current.bricks.color,
      roughnessMap: texturesRef.current.bricks.roughness,
      normalMap: texturesRef.current.bricks.normal,
      normalScale: new THREE.Vector2(1.5, 1.5),
      roughness: materialProps.roughness,
      metalness: materialProps.metalness,
    });

    // Material PBR para el cubo (Metal 034)
    const metal034Material = new THREE.MeshStandardMaterial({
      map: texturesRef.current.metal034.color,
      roughnessMap: texturesRef.current.metal034.roughness,
      metalnessMap: texturesRef.current.metal034.metalness,
      normalMap: texturesRef.current.metal034.normal,
      normalScale: new THREE.Vector2(1.5, 1.5),
      roughness: materialProps.roughness,
      metalness: materialProps.metalness,
    });

    // Material PBR para el cilindro (Metal 049)
    const metal049Material = new THREE.MeshStandardMaterial({
      map: texturesRef.current.metal049.color,
      roughnessMap: texturesRef.current.metal049.roughness,
      metalnessMap: texturesRef.current.metal049.metalness,
      normalMap: texturesRef.current.metal049.normal,
      normalScale: new THREE.Vector2(1.5, 1.5),
      roughness: materialProps.roughness,
      metalness: materialProps.metalness,
    });

    // Guardar materiales para actualizarlos luego
    materialsRef.current = {
      bricks: bricksMaterial,
      metal034: metal034Material,
      metal049: metal049Material,
    };

    // Actualizar materiales si existen las referencias
    if (spherePBRRef.current) {
      spherePBRRef.current.material = bricksMaterial;
    }
    if (cubeRef.current) {
      cubeRef.current.material = metal034Material;
    }
    if (cylinderRef.current) {
      cylinderRef.current.material = metal049Material;
    }
  }, [materialProps.roughness, materialProps.metalness]);

  // Inicializar GUI
  useEffect(() => {
    if (guiRef.current) {
      guiRef.current.destroy();
    }

    const gui = new GUI({ title: 'Material Properties' });
    guiRef.current = gui;

    const folder = gui.addFolder('PBR Settings');
    folder.open();

    folder.add(materialProps, 'roughness', 0, 1, 0.01).onChange((value) => {
      setMaterialProps((prev) => ({ ...prev, roughness: value }));
    });

    folder.add(materialProps, 'metalness', 0, 1, 0.01).onChange((value) => {
      setMaterialProps((prev) => ({ ...prev, metalness: value }));
    });

    folder.add(materialProps, 'lightIntensity', 0, 5, 0.1).onChange((value) => {
      setMaterialProps((prev) => ({ ...prev, lightIntensity: value }));
    });

    return () => {
      if (guiRef.current) {
        guiRef.current.destroy();
      }
    };
  }, []);

  return (
    <>
      {/* Plano base */}
      <mesh position={[0, -2, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color={0x222222} roughness={0.8} />
      </mesh>

      {/* Grid */}
      <Grid
        args={[20, 20]}
        cellSize={1}
        cellColor="#6f6f6f"
        sectionSize={5}
        sectionColor="#9d4edd"
        fadeStrength={1}
        fadeDistance={100}
      />

      {/* Esfera con material PBR - Texturas Bricks */}
      <mesh
        ref={spherePBRRef}
        position={[-4, 0, 0]}
        castShadow
        receiveShadow
      >
        <sphereGeometry args={[1.5, 64, 64]} />
        <meshStandardMaterial
          map={texturesRef.current.bricks?.color}
          roughnessMap={texturesRef.current.bricks?.roughness}
          normalMap={texturesRef.current.bricks?.normal}
          normalScale={new THREE.Vector2(1.5, 1.5)}
          roughness={materialProps.roughness}
          metalness={materialProps.metalness}
        />
      </mesh>

      {/* Cubo con material PBR - Texturas Metal 034 */}
      <mesh
        ref={cubeRef}
        position={[0, 0, 0]}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[1.5, 1.5, 1.5]} />
        <meshStandardMaterial
          map={texturesRef.current.metal034?.color}
          roughnessMap={texturesRef.current.metal034?.roughness}
          metalnessMap={texturesRef.current.metal034?.metalness}
          normalMap={texturesRef.current.metal034?.normal}
          normalScale={new THREE.Vector2(1.5, 1.5)}
          roughness={materialProps.roughness}
          metalness={materialProps.metalness}
        />
      </mesh>

      {/* Cilindro con material PBR - Texturas Metal 049 */}
      <mesh
        ref={cylinderRef}
        position={[4, 0, 0]}
        castShadow
        receiveShadow
      >
        <cylinderGeometry args={[1, 1.5, 2, 32]} />
        <meshStandardMaterial
          map={texturesRef.current.metal049?.color}
          roughnessMap={texturesRef.current.metal049?.roughness}
          metalnessMap={texturesRef.current.metal049?.metalness}
          normalMap={texturesRef.current.metal049?.normal}
          normalScale={new THREE.Vector2(1.5, 1.5)}
          roughness={materialProps.roughness}
          metalness={materialProps.metalness}
        />
      </mesh>

      {/* Etiquetas de texto para identificar objetos */}
      <TextLabel position={[-4, 2.5, 0]} text="Bricks092" />
      <TextLabel position={[0, 2.5, 0]} text="Metal034" />
      <TextLabel position={[4, 2.5, 0]} text="Metal049A" />
    </>
  );
};

// Componente auxiliar para etiquetas de texto
function TextLabel({ position, text }) {
  return (
    <mesh position={position}>
      <planeGeometry args={[2, 1]} />
      <meshBasicMaterial transparent opacity={0} />
    </mesh>
  );
}

export default PBRMaterialScene;
