import * as THREE from 'three';
import * as dat from 'dat.gui';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import * as LAMBERT from './Materials/lambert'
import * as PHONG from './Materials/phong'
import * as BLINN from './Materials/blinn'
import { probeAsync } from 'three/src/utils.js';

// Escena
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x202020);

// Cámara
const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.set(0, 0, 5);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth - 15, window.innerHeight - 15);
document.body.appendChild(renderer.domElement);

// Controles de cámara
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// GUI
const gui = new dat.GUI();

const params = {
  shininess: 32,
  color: '#aaaaaa',
  useBuiltIn: false
}

// ======================
// 💡 Luz real
// ======================
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(3, 3, 3);
scene.add(light);

// ======================
// 🔵 Representación visual de la luz
// ======================
const lightSphere = new THREE.Mesh(
  new THREE.SphereGeometry(0.1, 16, 16),
  new THREE.MeshBasicMaterial({ color: 0xffffff })
);
lightSphere.position.copy(light.position);
scene.add(lightSphere);

// ======================
// 🎮 Movimiento de la luz 
// ======================
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

let dragging = false;

const dragPlane = new THREE.Plane();
const planeNormal = new THREE.Vector3(0, 0, 1); // puedes cambiarlo luego

renderer.domElement.addEventListener('mousedown', (event) => {
  updateMouse(event);

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObject(lightSphere);

  if (intersects.length > 0) {
    dragging = true;
    controls.enabled = !dragging;

    // Definir plano de movimiento (perpendicular a la cámara)
    planeNormal.copy(camera.getWorldDirection(new THREE.Vector3()));
    dragPlane.setFromNormalAndCoplanarPoint(
      planeNormal,
      lightSphere.position
    );
  }
});

renderer.domElement.addEventListener('mousemove', (event) => {
  if (!dragging) return;

  updateMouse(event);

  raycaster.setFromCamera(mouse, camera);

  const intersection = new THREE.Vector3();
  raycaster.ray.intersectPlane(dragPlane, intersection);

  if (intersection) {
    light.position.copy(intersection);
    lightSphere.position.copy(intersection);
  }
});

renderer.domElement.addEventListener('mouseup', () => {
  dragging = false;
  controls.enabled = true;
});

function updateMouse(event) {
  const rect = renderer.domElement.getBoundingClientRect();

  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
}

// ======================
// 🪨 Materiales
// ======================
const builtLambert = new THREE.MeshLambertMaterial({
  color: 0xaaaaaa
});

const builtPhong = new THREE.MeshPhongMaterial({
  color: 0xaaaaaa,
  shininess: params.shininess
});

const pbrMaterial = new THREE.MeshStandardMaterial({
  color: 0xaaaaaa,
  metalness: 0.5,
  roughness: 0.5
});

const lambertMaterial = new THREE.ShaderMaterial({
  uniforms: {
    lightPosition: { value: light.position },
    color: { value: new THREE.Color(0xaaaaaa) }
  },
  vertexShader: LAMBERT.vertexShader,
  fragmentShader: LAMBERT.fragmentShader
});

const phongMaterial = new THREE.ShaderMaterial({
  uniforms: {
    lightPosition: { value: light.position },
    viewPosition: { value: camera.position },
    color: { value: new THREE.Color(0xaaaaaa) },
    shininess: { value: 32.0 }
  },
  vertexShader: PHONG.vertexShader,
  fragmentShader : PHONG.fragmentShader
});

const blinnMaterial = new THREE.ShaderMaterial({
  uniforms: {
    lightPosition: { value: light.position },
    viewPosition: { value: camera.position },
    color: { value: new THREE.Color(0xaaaaaa) },
    shininess: { value: 32.0 }
  },
  vertexShader: BLINN.vertexShader,
  fragmentShader: BLINN.fragmentShader
});

// ======================
// 🌍 Objetos principal
// ======================
const geometry = new THREE.SphereGeometry(1, 64, 64);
const lambSphere = new THREE.Mesh(geometry, lambertMaterial);
lambSphere.position.set(-3,0,0);
scene.add(lambSphere);

const phoSphere = new THREE.Mesh(geometry, phongMaterial);
phoSphere.position.set(0,0,0);
scene.add(phoSphere)

const blinSphere = new THREE.Mesh(geometry, blinnMaterial);
blinSphere.position.set(3,0,0);
scene.add(blinSphere)

// ======================
// 🎛️ Params
// ======================
gui.add(params, 'shininess', 1, 128).onChange(value => {
  phongMaterial.uniforms.shininess.value = value;
  blinnMaterial.uniforms.shininess.value = value;

  builtPhong.shininess = params.shininess;
});

gui.addColor(params, 'color').onChange(value => {
  lambertMaterial.uniforms.color.value.set(value);
  phongMaterial.uniforms.color.value.set(value);
  blinnMaterial.uniforms.color.value.set(value);

  builtLambert.color.set(params.color);
  builtPhong.color.set(params.color); 
  pbrMaterial.color.set(params.color);
});

gui.add(params, 'useBuiltIn').name('Built-in materials')
  .onChange(value => {
    if (value) {
      lambSphere.material = builtLambert;
      phoSphere.material = builtPhong;
      blinSphere.material = pbrMaterial;
    } else {
      lambSphere.material = lambertMaterial;
      phoSphere.material = phongMaterial;
      blinSphere.material = blinnMaterial;
    }
  });

// ======================
// 🔁 Main Loop 
// ======================
function animate() {
  requestAnimationFrame(animate);

  lambertMaterial.uniforms.lightPosition.value = light.position;
  phongMaterial.uniforms.lightPosition.value = light.position;
  phongMaterial.uniforms.viewPosition.value = camera.position;  
  blinnMaterial.uniforms.lightPosition.value = light.position;
  blinnMaterial.uniforms.viewPosition.value = camera.position;

  controls.update();
  renderer.render(scene, camera);
}

animate();