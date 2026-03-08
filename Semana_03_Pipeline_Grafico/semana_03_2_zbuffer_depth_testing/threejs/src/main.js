import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* =========================================================
   SCENE
========================================================= */
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x202020);

/* =========================================================
   CAMERA (near / far son CLAVE para el depth buffer)
========================================================= */
const camera = new THREE.PerspectiveCamera(
  60,                               // FOV
  window.innerWidth / window.innerHeight,
  0.1,                              // near  (prueba 0.01)
  50                                // far   (prueba 1000)
);

camera.position.set(0, 0, 12);

/* =========================================================
   RENDERER
========================================================= */
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

/* =========================================================
   DEPTH TEST (activar / desactivar para comparar)
========================================================= */
// renderer.getContext().disable(renderer.getContext().DEPTH_TEST);
renderer.getContext().enable(renderer.getContext().DEPTH_TEST);

/* =========================================================
   CONTROLS (para moverte por la escena)
========================================================= */
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

/* =========================================================
   COLOR MATERIAL
========================================================= */
function randomColor() {
  return new THREE.Color(
    Math.random(),
    Math.random(),
    Math.random()
  );
}

/* =========================================================
   SHADER MATERIAL – VISUALIZACIÓN DEL DEPTH BUFFER
========================================================= */
const depthMaterial = new THREE.ShaderMaterial({
  vertexShader: `
    void main() {
      gl_Position = projectionMatrix *
                    modelViewMatrix *
                    vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    void main() {
      float depth = gl_FragCoord.z;
      depth = pow(depth, 20.0); // exagera diferencias
      vec3 color = vec3(1.0, 0.4, 0.2);
      gl_FragColor = vec4(color * depth, 1.0);
    }
  `,
  depthTest: true,
  depthWrite: true
});

/* =========================================================
   OBJECTS A DIFERENTES PROFUNDIDADES
========================================================= */
const geometry = new THREE.BoxGeometry(2, 2, 2);

// Z posiciones distintas (profundidad)
const zPositions = [-6, -3, 0, 3, 6];
const meshes = []
const colorMaterials = [];

zPositions.forEach((z) => {
  const colorMaterial = new THREE.MeshBasicMaterial({
    color: randomColor()
  });

  const mesh = new THREE.Mesh(geometry, colorMaterial);
  mesh.position.z = z;

  mesh.userData.colorMaterial = colorMaterial;

  colorMaterials.push(colorMaterial);
  meshes.push(mesh);
  scene.add(mesh);
});

/* =========================================================
   REFERENCIA VISUAL (ejes)
========================================================= */
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper);

/* =========================================================
   BUTTONS 
========================================================= */
let depthEnabled = true;
let showDepth = true;

document.getElementById('toggleDepth').onclick = () => {
  depthEnabled = !depthEnabled;

  meshes.forEach(mesh => {
    mesh.material.depthTest = depthEnabled;
    mesh.material.needsUpdate = true;
  });

  console.log('Depth Test:', depthEnabled);
};

document.getElementById('toggleMaterial').onclick = () => {
  showDepth = !showDepth;

  meshes.forEach(mesh => {
    mesh.material = showDepth ? depthMaterial : mesh.userData.colorMaterial;
  });

  console.log('Depth View:', showDepth);
};

/* =========================================================
   RESIZE
========================================================= */
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

/* =========================================================
   LOOP DE RENDER
========================================================= */
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

animate();
