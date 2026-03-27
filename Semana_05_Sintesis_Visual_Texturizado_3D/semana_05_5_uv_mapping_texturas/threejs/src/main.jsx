import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

// Escena
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111111);

// Cámara
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.set(3, 3, 3);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Controles
const controls = new OrbitControls(camera, renderer.domElement);

// Luces
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 1);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);

// Textura UV test
const textureLoader = new THREE.TextureLoader();
const texture = textureLoader.load("/uv-test.png");

texture.wrapS = THREE.RepeatWrapping;
texture.wrapT = THREE.RepeatWrapping;

// Loader GLTF
const loader = new GLTFLoader();

let model;

loader.load(
  "/src/assets/figures.glb",
  (gltf) => {
    model = gltf.scene;

    model.traverse((child) => {
      if (child.isMesh) {
        child.material = new THREE.MeshStandardMaterial({
          map: texture,
        });
      }
    });

    scene.add(model);
  },
  undefined,
  (error) => {
    console.error("Error cargando modelo:", error);
  }
);

// 🔥 MODOS
let mode = "normal";

window.addEventListener("keydown", (e) => {
  if (e.key === "1") mode = "normal";
  if (e.key === "2") mode = "repeat";
  if (e.key === "3") mode = "offset";
  if (e.key === "4") mode = "wrap";
  if (e.key === "5") mode = "scale";

  applyMode();
});

function applyMode() {
  if (!model) return;

  texture.repeat.set(1, 1);
  texture.offset.set(0, 0);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.RepeatWrapping;
  texture.needsUpdate = true;

  if (mode === "repeat") {
    texture.repeat.set(8, 8);
  }

  if (mode === "offset") {
    texture.offset.set(0.5, 0.5);
  }

  if (mode === "wrap") {
    texture.wrapS = THREE.MirroredRepeatWrapping;
    texture.wrapT = THREE.ClampToEdgeWrapping;
  }

  if (mode === "scale") {
    model.scale.set(3, 1, 0.3);
  } else {
    model.scale.set(1, 1, 1);
  }
}

// Resize
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Animación
function animate() {
  requestAnimationFrame(animate);

  renderer.render(scene, camera);
}

animate();