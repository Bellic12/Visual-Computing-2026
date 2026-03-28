# Additional Resources & Customization

## 🎨 Color Palette Reference

### Current Theme
```
Primary: #9d4edd (Purple)
Secondary: #3c096c (Dark Purple)
Accent: #5a189a (Vibrant Purple)
Text: #f8f9fa (Off-white)
Background: #0f0e17 (Very Dark)
```

### Alternative Themes

#### Dark Mode (Current)
```css
--primary-color: #9d4edd;
--secondary-color: #3c096c;
--accent-color: #5a189a;
--text-color: #f8f9fa;
--bg-dark: #0f0e17;
```

#### Ocean Theme
```css
--primary-color: #00b4d8;
--secondary-color: #0077b6;
--accent-color: #0096c7;
--text-color: #ffffff;
--bg-dark: #001d3d;
```

#### Forest Theme
```css
--primary-color: #52b788;
--secondary-color: #1b4332;
--accent-color: #2d6a4f;
--text-color: #f1faee;
--bg-dark: #081c15;
```

---

## 🔧 Performance Optimization Tips

### Level 1: Basic
```javascript
// In PBRMaterialScene.jsx
// Reduce sphere quality
<sphereGeometry args={[1.5, 32, 32]} />  // From 64, 64

// Disable shadows
directionalLight.castShadow = false;

// Reduce texture resolution
canvas.width = 256;   // From 512
canvas.height = 256;
```

### Level 2: Aggressive
```javascript
// Use simpler materials
const basicMaterial = new THREE.MeshBasicMaterial({
  color: 0x888888,
  // No texture maps
});

// Reduce group segments
<planeGeometry args={[20, 20, 4, 4]} />  // Add segments

// Lower shadow resolution
directionalLight.shadow.mapSize.width = 1024;
directionalLight.shadow.mapSize.height = 1024;
```

### Level 3: Extreme
```javascript
// Remove non-essential objects
// Keep only one comparison sphere

// Use mobile-friendly resolution
canvas.width = 128;
canvas.height = 128;

// Single light source
scene.children = scene.children.filter(
  child => child instanceof THREE.Light && !isFillLight
);
```

---

## 📚 Learning Path

### Day 1: Setup & Basics
- [ ] Install Node.js
- [ ] Create project with Vite
- [ ] Create first Three.js scene
- [ ] Add lighting

### Day 2: Materials & Textures
- [ ] Learn about materials
- [ ] Create procedural textures
- [ ] Apply textures to objects
- [ ] Understand PBR

### Day 3: Interactivity & UI
- [ ] Add OrbitControls
- [ ] Integrate lil-gui
- [ ] Create dynamic controls
- [ ] Update materials in real-time

### Day 4: Polish & Documentation
- [ ] Add styling
- [ ] Responsive design
- [ ] Write documentation
- [ ] Capture screenshots

### Day 5: Deployment & Presentation
- [ ] Build for production
- [ ] Deploy (Vercel, Netlify)
- [ ] Create commits
- [ ] Final documentation

---

## 🚀 Advanced Customization

### Add More Geometries

In `PBRMaterialScene.jsx`:

```javascript
// Add a Torus
<mesh position={[0, 0, 4]} castShadow receiveShadow>
  <torusGeometry args={[1, 0.3, 32, 100]} />
  <meshStandardMaterial
    map={texturesRef.current.color}
    roughness={materialProps.roughness}
    metalness={materialProps.metalness}
  />
</mesh>

// Add a Cone
<mesh position={[-4, 0, -4]} castShadow receiveShadow>
  <coneGeometry args={[1, 2, 32]} />
  <meshStandardMaterial
    map={texturesRef.current.color}
    roughness={materialProps.roughness}
  />
</mesh>

// Add a Cylinder
<mesh position={[4, 0, -4]} castShadow receiveShadow>
  <cylinderGeometry args={[1, 1, 2, 32]} />
  <meshStandardMaterial
    map={texturesRef.current.color}
    metalness={materialProps.metalness}
  />
</mesh>
```

### Change Lighting

```javascript
// More dramatic lighting
const directionalLight = new THREE.DirectionalLight(0xffffff, 4);
directionalLight.position.set(20, 30, 20);

// Add colored lights
const redLight = new THREE.DirectionalLight(0xff0000, 0.2);
redLight.position.set(-10, 5, 0);
scene.add(redLight);

const blueLight = new THREE.DirectionalLight(0x0000ff, 0.2);
blueLight.position.set(0, 5, -10);
scene.add(blueLight);
```

### Custom Material Colors

```javascript
// Change procedural texture generation
const createCustomTexture = () => {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  
  // Your custom algorithm here
  for (let i = 0; i < canvas.width; i++) {
    for (let j = 0; j < canvas.height; j++) {
      // Custom colors
      ctx.fillStyle = `hsl(${i % 360}, 100%, 50%)`;
      ctx.fillRect(i, j, 1, 1);
    }
  }
  
  return new THREE.CanvasTexture(canvas);
};
```

---

## 🎯 Debugging Utilities

### Add Stats Monitor

```bash
npm install three/examples -D
```

Then in `PBRMaterialScene.jsx`:

```javascript
import Stats from 'three/examples/jsm/libs/stats.module.js';

useEffect(() => {
  const stats = Stats();
  stats.domElement.style.position = 'absolute';
  stats.domElement.style.top = '0px';
  document.body.appendChild(stats.domElement);

  // Update in animation loop
  const frame = () => {
    stats.update();
    renderer.render(scene, camera);
    requestAnimationFrame(frame);
  };
}, []);
```

### Console Logging

```javascript
// Log material properties
console.log('Material Props:', materialProps);

// Log scene information
console.log('Scene children:', scene.children);

// Log camera position
console.log('Camera position:', camera.position);
```

### Performance Monitoring

```javascript
// In browser console
console.time('renderFrame');
renderer.render(scene, camera);
console.timeEnd('renderFrame');

// Check memory
console.log(renderer.info);
```

---

## 📊 Texture Customization

### Create Gradient Texture

```javascript
const createGradientTexture = () => {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, 512, 512);
  gradient.addColorStop(0, '#000000');
  gradient.addColorStop(0.5, '#888888');
  gradient.addColorStop(1, '#ffffff');

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 512, 512);

  return new THREE.CanvasTexture(canvas);
};
```

### Create Checkerboard Texture

```javascript
const createCheckerboardTexture = () => {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  const squareSize = 64;
  for (let i = 0; i < 512; i += squareSize) {
    for (let j = 0; j < 512; j += squareSize) {
      if (((i / squareSize) + (j / squareSize)) % 2 === 0) {
        ctx.fillStyle = '#ffffff';
      } else {
        ctx.fillStyle = '#000000';
      }
      ctx.fillRect(i, j, squareSize, squareSize);
    }
  }

  return new THREE.CanvasTexture(canvas);
};
```

### Create Noise Texture

```javascript
const createNoiseTexture = () => {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  
  const imageData = ctx.createImageData(512, 512);
  const data = imageData.data;

  // Perlin noise or simple random
  for (let i = 0; i < data.length; i += 4) {
    const value = Math.random() * 255;
    data[i] = value;     // R
    data[i + 1] = value; // G
    data[i + 2] = value; // B
    data[i + 3] = 255;   // A
  }

  ctx.putImageData(imageData, 0, 0);
  return new THREE.CanvasTexture(canvas);
};
```

---

## 🎬 Animation Ideas

### Rotating Camera

```javascript
useFrame(() => {
  const angle = Math.atan2(camera.position.y, camera.position.x);
  const radius = Math.sqrt(
    camera.position.x ** 2 + camera.position.y ** 2
  );
  
  camera.position.x = radius * Math.cos(angle + 0.001);
  camera.position.z = radius * Math.sin(angle + 0.001);
});
```

### Pulsing Light

```javascript
useFrame(({ clock }) => {
  const intensity = 2.5 + Math.sin(clock.getElapsedTime()) * 0.5;
  directionalLight.intensity = intensity;
});
```

### Rotating Objects

```javascript
<mesh rotation={[0, clock.getElapsedTime(), 0]}>
  <sphereGeometry args={[1.5, 64, 64]} />
  <meshStandardMaterial />
</mesh>
```

---

## 🔗 External Assets

### Free PBR Texture Sites

1. **ambientCG** - https://ambientcg.com/
2. **Poly Haven** - https://polyhaven.com/
3. **Textures.com** - https://www.textures.com/
4. **FreePBR** - https://freepbr.com/
5. **CGBooksOnline** - https://cgbooksonline.com/

### How to Use External Textures

```javascript
const textureLoader = new THREE.TextureLoader();

// Load from URL
const colorTexture = textureLoader.load(
  'https://example.com/color.jpg'
);
const roughnessTexture = textureLoader.load(
  'https://example.com/roughness.jpg'
);

// Use in material
const material = new THREE.MeshStandardMaterial({
  map: colorTexture,
  roughnessMap: roughnessTexture,
});
```

---

## 📱 Mobile Optimization

### Responsive Canvas

```javascript
const handleResize = () => {
  const width = window.innerWidth;
  const height = window.innerHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
};

window.addEventListener('resize', handleResize);
```

### Touch Controls

```javascript
// Already handled by OrbitControls with touch support
// No additional code needed
```

### Mobile Settings

```javascript
const isMobile = window.innerWidth < 768;

const sphereSegments = isMobile ? 32 : 64;

<sphereGeometry args={[1.5, sphereSegments, sphereSegments]} />
```

---

## 🎨 CSS Customization

### Change Theme Colors

Edit `App.css`:

```css
:root {
  --primary-color: #your-color;
  --secondary-color: #your-color;
  --accent-color: #your-color;
  --text-color: #your-color;
  --bg-dark: #your-color;
}
```

### Custom Fonts

```css
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

* {
  font-family: 'Poppins', sans-serif;
}
```

### Dark/Light Mode Toggle

```javascript
const [isDarkMode, setIsDarkMode] = useState(true);

useEffect(() => {
  document.body.classList.toggle('dark-mode', isDarkMode);
  document.body.classList.toggle('light-mode', !isDarkMode);
}, [isDarkMode]);
```

---

## 🔐 Production Build

### Optimize Build

In `vite.config.js`:

```javascript
export default {
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console logs
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          three: ['three', '@react-three/fiber'],
        },
      },
    },
  },
};
```

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm run build
netlify deploy --prod --dir=dist
```

---

## 📖 Reading Recommendations

- "Real-Time Rendering" by Akenine-Möller & Haines
- "WebGL Programming Guide" 
- Three.js Documentation
- React Three Fiber Docs

---

## 🎓 Educational Extensions

### Propose Extensions to Prof
1. Add more complex geometries
2. Implement texture painting tool
3. Create material preset library
4. Add animation system
5. Implement physics simulation
6. Create AR viewer

---

**Resources Guide Updated:** March 28, 2026  
**Version:** 1.0  
**Status:** Ready ✅
