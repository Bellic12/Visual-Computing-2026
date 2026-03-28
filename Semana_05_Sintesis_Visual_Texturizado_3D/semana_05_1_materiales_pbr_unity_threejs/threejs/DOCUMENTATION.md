# Three.js PBR Materials Implementation

## 📖 Documentación Técnica

### Descripción General

Esta es una implementación educativa de **Physically-Based Rendering (PBR)** usando **Three.js** con **React Three Fiber**. El proyecto demuestra conceptos fundamentales de renderizado realista mediante la comparación entre materiales PBR (con texturas) y materiales básicos.

---

## 🎯 Características Principales

### 1. **Escena 3D Interactiva**
- Luz ambiental + luz direccional + luz de relleno
- Plano base para recibir sombras
- Grid de referencia visual
- OrbitControls para exploración

### 2. **Materiales PBR Avanzados**
```javascript
MeshStandardMaterial {
  map: Albedo/Base Color,
  roughnessMap: Surface smoothness,
  metalnessMap: Metallic properties,
  normalMap: Surface details,
  normalScale: Normal intensity
}
```

### 3. **Panel de Controles Dinámicos**
- Ajuste de roughness en tiempo real
- Control de metalness
- Control de intensidad de luz
- Actualización instantánea de la escena

### 4. **Texturas Procedurales**
- Generadas con Canvas 2D
- Sin dependencias de archivos externos
- Algorítmicamente correctas para demostración

---

## 🔧 Componentes Principales

### `App.jsx` - Componente Raíz
```javascript
// Estructura principal
<Canvas>
  <PerspectiveCamera />
  <OrbitControls />
  <PBRMaterialScene />
</Canvas>
```

**Responsabilidades:**
- Configurar canvas de Three.js
- Controlar layout general
- Mostrar información del usuario

### `PBRMaterialScene.jsx` - Lógica Principal
```javascript
// Estructura interna
1. Generación de texturas procedurales
2. Configuración de iluminación
3. Creación de materiales
4. Instanciación de geometrías
5. Inicialización de GUI
```

**Hooks utilizados:**
- `useThree()` - Acceso a escena y renderer
- `useEffect()` - Inicialización y cleanup
- `useRef()` - Referencias a objetos persistentes
- `useState()` - Estado de propiedades

---

## 🎨 Generación de Texturas

### Función Core: `createProceduralTexture(type)`

```javascript
const createProceduralTexture = (type) => {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  
  switch(type) {
    case 'color':     // Base color con variación
    case 'roughness': // Valores de aspereza
    case 'metalness': // Puntos metálicos
    case 'normal':    // Mapa de relieve
  }
  
  return new THREE.CanvasTexture(canvas);
};
```

**Características:**
- Resolución 512x512 (balance calidad/performance)
- Algoritmos simples pero efectivos
- Determinísticos (reproducibles)

### Tipos de Texturas

#### 1. **Color (Albedo)**
```javascript
// Patrón basado en funciones trigonométricas
const noise = Math.sin(i * 0.01) * Math.cos(j * 0.01);
const value = Math.floor(150 + noise * 50);
// Resultado: Tonos grises con variación suave
```

#### 2. **Roughness**
```javascript
// Ruido aleatorio controlado
const value = Math.floor(Math.random() * 100 + 80);
// Resultado: Variación de 80-180 en escala 0-255
```

#### 3. **Metalness**
```javascript
// Fondo oscuro con detalles brillantes
ctx.fillStyle = '#1a1a1a';  // Base oscura
// Puntos blancos aleatorios para metalidad
```

#### 4. **Normal Map**
```javascript
// Patrón de bloques en RGB
// R: Información X, G: Información Y, B: Información Z
// Simula relieves sin geometría adicional
```

---

## 💡 Sistema de Iluminación

### Configuración Triple de Luces

| Luz | Tipo | Posición | Intensidad | Propósito |
|-----|------|----------|-----------|----------|
| Ambiental | AmbientLight | Global | 0.5 | Iluminación base |
| Principal | DirectionalLight | (10, 15, 10) | 2.5 (configurable) | Luz principal direccional |
| Relleno | DirectionalLight | (-10, 5, -10) | 0.3 | Relleno de sombras |

### Sombras

```javascript
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
// Sombras de alta resolución para realismo
```

---

## 🎛️ Panel de Controles (lil-gui)

### Propiedades Controlables

```javascript
{
  roughness: 0-1,        // Aspereza de superficie
  metalness: 0-1,        // Apariencia metálica
  lightIntensity: 0-5    // Intensidad de luz direccional
}
```

### Implementación

```javascript
const folder = gui.addFolder('PBR Settings');
folder.add(materialProps, 'roughness', 0, 1, 0.01)
      .onChange((value) => updateMaterial(value));
```

**Características:**
- Actualización en tiempo real
- Incrementos de 0.01 para precisión
- Rango limitado según física

---

## 📐 Geometrías en Escena

### Objetos del Mundo

```
Escena
├── Plano Base (20x20)
│   └── Recibe sombras
├── Grid de Referencia
│   └── Ayuda visual
├── Esfera PBR (r=1.5)
│   ├── Material: MeshStandardMaterial
│   ├── Texturas: Color + Rough + Metal + Normal
│   └── Posición: (-3, 0, 0)
├── Esfera Básica (r=1.5)
│   ├── Material: MeshPhongMaterial
│   ├── Color: Gris uniforme
│   └── Posición: (3, 0, 0)
└── Cubo PBR (1.5x1.5x1.5)
    ├── Material: MeshStandardMaterial
    ├── Texturas: Completas
    └── Posición: (0, 0, -4)
```

### Configuración de Geometría

```javascript
sphereGeometry.args = [radius, widthSegments, heightSegments]
// [1.5, 64, 64] - Balance calidad/performance
```

---

## 🚀 Ciclo de Vida de Componentes

### Inicialización (useEffect #1)
```javascript
// Cargar texturas procedurales
useEffect(() => {
  texturesRef.current = {
    color: createProceduralTexture('color'),
    roughness: createProceduralTexture('roughness'),
    metalness: createProceduralTexture('metalness'),
    normal: createProceduralTexture('normal'),
  };
}, []);
```

### Configuración de Luces (useEffect #2)
```javascript
// Agregar luces a la escena
useEffect(() => {
  scene.add(ambientLight);
  scene.add(directionalLight);
  scene.add(fillLight);
}, [materialProps.lightIntensity, scene]);
```

### Actualización de Materiales (useEffect #3)
```javascript
// Actualizar propiedades de material
useEffect(() => {
  pbrMaterial.roughness = materialProps.roughness;
  pbrMaterial.metalness = materialProps.metalness;
}, [materialProps.roughness, materialProps.metalness]);
```

### Inicialización de GUI (useEffect #4)
```javascript
// Crear panel de controles
useEffect(() => {
  const gui = new GUI();
  gui.add(materialProps, 'roughness', 0, 1, 0.01);
  // ... más controles
  return () => gui.destroy(); // Cleanup
}, []);
```

---

## 🔄 Flujo de Datos

```
User Input (GUI)
      ↓
setState(materialProps)
      ↓
Component Re-render
      ↓
useEffect Dependencies
      ↓
Update Materials/Lights
      ↓
Three.js Render
      ↓
Canvas Update
```

---

## 🎯 Argumentos de Geometría

### Sphere
```javascript
sphereGeometry(
  radius = 1.5,        // Radio de la esfera
  widthSegments = 64,  // Segmentos horizontales
  heightSegments = 64  // Segmentos verticales
)
// Mayor segmentación = más suave pero más lento
```

### Box
```javascript
boxGeometry(
  width = 1.5,   // Ancho (X)
  height = 1.5,  // Alto (Y)
  depth = 1.5    // Profundidad (Z)
)
```

### Plane
```javascript
planeGeometry(
  width = 20,    // Ancho (X)
  height = 20    // Alto (Z)
)
```

---

## 🎨 Materiales Utilizados

### MeshStandardMaterial (PBR)
```javascript
new THREE.MeshStandardMaterial({
  map: colorTexture,
  roughnessMap: roughnessTexture,
  metalnessMap: metalnessTexture,
  normalMap: normalTexture,
  normalScale: new Vector2(0.5, 0.5),
  emissive: 0x000000,
  emissiveIntensity: 0,
  roughness: 0.5,
  metalness: 0.5,
})
```

**Parámetros clave:**
- `roughness`: Valor base (0=espejo, 1=mate)
- `metalness`: Valor base (0=no-metal, 1=metal)
- `normalScale`: Intensidad del efecto normal
- `map`: Textura de color base

### MeshPhongMaterial (Comparación)
```javascript
new THREE.MeshPhongMaterial({
  color: 0x888888,
  shininess: 100,
  emissive: 0x000000,
})
```

**Diferencia:**
- No usa mapas de texturas
- Iluminación simplificada
- Útil para comparación visual

---

## 📊 Rendimiento

### Optimizaciones Aplicadas

1. **Texturas Procedurales**
   - Sin descarga de archivos
   - Generadas una sola vez en useEffect
   - Reutilizadas en todos los objetos

2. **Shadow Maps**
   - Resolución equilibrada (2048x2048)
   - Solo luces directionales proyectan sombras
   - Optimizadas según distancia

3. **Geometría**
   - 64x64 segmentos es balance realismo/performance
   - Plano base sin segmentación innecesaria
   - Reuse de geometrías/materiales

4. **Cleanup**
   - GUI destruida en cleanup
   - Texturas reutilizadas (Sin memory leak)
   - Escena limpiada antes de reagregar luces

---

## 🐛 Debugging Tips

### Ver en DevTools Three.js
```javascript
// En consola del navegador
import { renderer, scene } from 'THREE';
scene.children.forEach(child => console.log(child));
```

### Verificar Texturas
```javascript
// Ver texturas cargadas
console.log(texturesRef.current);
```

### Monitorear Performance
```javascript
// Usar Stats.js para FPS
import Stats from 'three/examples/jsm/libs/stats.module.js';
```

---

## 📝 Notas Importantes

1. **Procedurales vs Reales**
   - Las texturas son procedurales por simplicidad
   - En producción usarías texturas reales (ambientCG, Poly Haven, etc.)

2. **Color Space**
   - Las texturas se suponen en sRGB
   - Three.js maneja conversión automáticamente

3. **Rendimiento en Móviles**
   - Considera reducir segmentación en mobile
   - Ajusta resolución de shadow maps
   - Usa media queries CSS

4. **Compatibilidad**
   - Requiere WebGL 2
   - Verificar soporte en navegador objetivo

---

## 🔗 Referencias de Código

### Cambiar tamaño de esfera
En `PBRMaterialScene.jsx`:
```javascript
<sphereGeometry args={[2, 32, 32]} />  // Radius=2, menos segmentos
```

### Cambiar posiciones
```javascript
<mesh position={[x, y, z]}>
  // x: izquierda/derecha
  // y: arriba/abajo
  // z: hacia/lejos
</mesh>
```

### Agregar nuevo control en GUI
```javascript
folder.add(materialProps, 'newProperty', minValue, maxValue, step)
      .onChange((value) => setMaterialProps(prev => ({...prev, newProperty: value})));
```

---

## ✅ Checklist de Funcionalidad

- [x] Escena PBR cargada correctamente
- [x] Texturas procedurales generadas
- [x] Materiales aplicados a geometrías
- [x] Iluminación configurada (3 luces)
- [x] GUI funcional con actualizaciones
- [x] Sombras dinámicas activas
- [x] OrbitControls interactivo
- [x] Responsive design
- [x] Sin memory leaks
- [x] Código comentado y estructurado

---

**Documento Actualizado:** 28 de Marzo, 2026  
**Versión:** 1.0  
**Estado:** Final ✅
