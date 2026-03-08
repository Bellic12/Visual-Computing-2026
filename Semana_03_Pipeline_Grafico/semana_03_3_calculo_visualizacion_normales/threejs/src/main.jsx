import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { VertexNormalsHelper } from 'three/examples/jsm/helpers/VertexNormalsHelper'
import vertexShader from './shaders/normalVertex.glsl?raw'
import fragmentShader from './shaders/normalFragment.glsl?raw'
import { computeNormalsManually } from './helpers/ManualNormals'

/* ───────── SCENE ───────── */
const scene = new THREE.Scene()
scene.background = new THREE.Color(0x202020)

/* ───────── CAMERA ───────── */
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  100
)
camera.position.set(2, 2, 3)

/* ───────── RENDERER ───────── */
const renderer = new THREE.WebGLRenderer({ antialias: true })
renderer.setSize(window.innerWidth, window.innerHeight)
document.getElementById('root').appendChild(renderer.domElement)

/* ───────── CONTROLS ───────── */
const controls = new OrbitControls(camera, renderer.domElement)

/* ───────── LIGHT ───────── */
const light = new THREE.DirectionalLight(0xffffff, 2)
scene.add(light)

/* ───────── GEOMETRY (procedural) ───────── */
const geometry = new THREE.BoxGeometry(1, 1, 1, 1, 1, 1)

/* Acceso directo a normales */
console.log('Normals attribute:', geometry.attributes.normal)

/* ───────── MANUAL NORMAL COMPUTATION ───────── */
/* Para el calculo manual hace falta convertir la figura a no indexada */
const geometryNI = geometry.toNonIndexed()
computeNormalsManually(geometryNI)

/* ───────── SMOOTH SHADING ───────── */
//geometry.computeVertexNormals()

/* ───────── MATERIAL ───────── */
const material = new THREE.MeshStandardMaterial({
  color: 0x44aa88,
  flatShading: false
})

const mesh = new THREE.Mesh(geometryNI, material)
scene.add(mesh)

/* ───────── VERTEX NORMALS HELPER ───────── */
const normalsHelper = new VertexNormalsHelper(mesh, 0.2, 0xff0000)
scene.add(normalsHelper)

/* ───────── NORMAL DIRECTION SHADER ───────── */
const normalShaderMaterial = new THREE.ShaderMaterial({
  vertexShader,
  fragmentShader
})

const shaderMesh = new THREE.Mesh(
  new THREE.SphereGeometry(0.5, 32, 32),
  normalShaderMaterial
)
shaderMesh.position.x = 2
scene.add(shaderMesh)

//const sphereHelper = new VertexNormalsHelper(shaderMesh, 0.2, 0xff0000)
//scene.add(sphereHelper)

/* ─────────   BUTTON    ───────── */
const button = document.getElementById('toggleAnim')

button.addEventListener('click', () => {
  isAnimating = !isAnimating
  button.textContent = isAnimating
    ? 'Pausar animación'
    : 'Reanudar animación'
})

/* ───────── RENDER LOOP ───────── */
let isAnimating = true
let angle = 0

function animate() {
  requestAnimationFrame(animate)
  
  if(isAnimating) {
    angle += 0.05
    light.position.set(
      Math.cos(angle) * 3,
      2,
      Math.sin(angle) * 3
    )
  }

  renderer.render(scene, camera)
}
animate()

/* ───────── RESIZE ───────── */
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
})
