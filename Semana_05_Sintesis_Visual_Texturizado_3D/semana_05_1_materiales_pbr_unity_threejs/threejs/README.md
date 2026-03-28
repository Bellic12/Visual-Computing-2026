# Three.js PBR Materials - Getting Started

## 🚀 Quick Start

### Installation

```bash
# Navigate to threejs folder
cd threejs

# Install dependencies
npm install

# Run development server
npm run dev
```

The application will automatically open at `http://localhost:3000`

---

## 📋 Project Structure

```
threejs/
├── src/
│   ├── components/
│   │   └── PBRMaterialScene.jsx      # Main scene implementation
│   ├── App.jsx                       # Root component
│   ├── App.css                       # Main styles
│   ├── index.jsx                     # Entry point
│   └── index.css                     # Global styles
├── index.html                        # HTML template
├── vite.config.js                    # Vite configuration
├── package.json                      # Dependencies
├── DOCUMENTATION.md                  # Technical documentation
└── .gitignore                        # Git ignore file
```

---

## 🛠️ Available Scripts

```bash
# Development server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🎮 How to Use the Application

### Camera Controls
- **Rotate:** Click and drag with left mouse button
- **Zoom:** Mouse wheel
- **Pan:** Right click and drag

### Interactive Controls (lil-gui Panel)

#### Roughness Slider
- **Range:** 0 to 1
- **Effect:** 
  - 0 = Mirror-like, highly reflective
  - 1 = Completely matte surface
- **Use:** Adjust to see how surface reflectivity changes

#### Metalness Slider
- **Range:** 0 to 1
- **Effect:**
  - 0 = Non-metallic material (plastic, rubber)
  - 1 = Pure metallic surface (gold, steel)
- **Use:** Change how metallic the material appears

#### Light Intensity Slider
- **Range:** 0 to 5
- **Effect:** Controls brightness of main directional light
- **Use:** Increase to see more dramatic lighting effects

### Scene Contents

1. **Left Sphere (Blue-ish)** - PBR Material with full textures
2. **Right Sphere (Gray)** - Basic Material without textures (Comparison)
3. **Central Cube** - PBR Material (Reference)
4. **Ground Plane** - Receives shadows from objects
5. **Purple Grid** - Reference for scene scale

---

## 💻 Dependencies Explained

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.2.0 | UI Framework |
| three | ^r150 | 3D Graphics Engine |
| @react-three/fiber | ^8.13.0 | React renderer for Three.js |
| @react-three/drei | ^9.88.0 | Useful components and helpers |
| lil-gui | ^0.19.1 | Interactive controls panel |
| vite | ^4.3.0 | Build tool and dev server |

---

## 🎨 Key Features

### ✅ Implemented

- [x] PBR Material with multiple texture maps
- [x] Procedurally generated textures
- [x] Real-time material property adjustment
- [x] Dual-light system (ambient + directional + fill)
- [x] Dynamic shadow mapping
- [x] Interactive camera controls
- [x] Responsive layout
- [x] GUI controls with lil-gui
- [x] Comparison between PBR and Basic materials

### 🚧 Future Enhancements

- [ ] Load external PBR textures
- [ ] Add more geometries (torus, cone, etc.)
- [ ] Implement Ambient Occlusion (AO)
- [ ] Image-Based Lighting (IBL)
- [ ] Model import (glTF/GLTF)
- [ ] Texture export/import
- [ ] Performance monitoring

---

## 📖 Understanding the Code

### Main Component Flow

```
App.jsx
└── Canvas (Vite + Three.js)
    └── PerspectiveCamera
    └── OrbitControls
    └── PBRMaterialScene
        ├── Ambient Light
        ├── Directional Light
        ├── Fill Light
        ├── Ground Plane
        ├── PBR Sphere (Left)
        ├── Basic Sphere (Right)
        ├── PBR Cube (Center)
        └── GUI Controls (lil-gui)
```

### Material Types Used

**MeshStandardMaterial** (PBR)
```javascript
// This is the physically-based material
// It follows realistic light interaction
// Used for both spheres and cube on the left/center
```

**MeshPhongMaterial** (Basic)
```javascript
// This is a simplified material
// Used for comparison (right sphere)
// Shows the difference without PBR
```

---

## 🔧 Customization Guide

### Change Material Properties

Edit `src/components/PBRMaterialScene.jsx`:

```javascript
// Change default roughness and metalness values
const [materialProps, setMaterialProps] = useState({
  roughness: 0.5,      // Change this value (0-1)
  metalness: 0.5,      // Change this value (0-1)
  lightIntensity: 2.5, // Change this value (0-5)
});
```

### Modify Light Positions

```javascript
// In the lighting configuration:
directionalLight.position.set(10, 15, 10);  // x, y, z
fillLight.position.set(-10, 5, -10);        // x, y, z
```

### Adjust Object Positions

```javascript
// Each mesh has a position prop:
<mesh position={[-3, 0, 0]}>  // [x, y, z]
```

### Change Geometry Sizes

```javascript
// Modify geometry arguments:
<sphereGeometry args={[1.5, 64, 64]} />
// [radius, widthSegments, heightSegments]
```

---

## 🐛 Troubleshooting

### Application won't start
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### GUI not showing
- Check if lil-gui is installed: `npm list lil-gui`
- Reinitialize with: `npm run dev`

### Performance issues
- Reduce sphere segments (64 → 32)
- Reduce shadow map resolution (2048 → 1024)
- Close GUI when not using

### Canvas not rendering
- Check browser console for errors
- Verify WebGL 2 support
- Try a different browser

---

## 🎓 Learning Resources

### PBR Theory
- [LearnOpenGL - PBR](https://learnopengl.com/PBR/Theory)
- [The PBR Book](https://pbr-book.org/)

### Three.js Documentation
- [Official Three.js Docs](https://threejs.org/docs/)
- [Three.js Examples](https://threejs.org/examples/)

### React Three Fiber
- [Documentation](https://docs.pmnd.rs/react-three-fiber/)
- [YouTube Tutorials](https://www.youtube.com/@pmndrs)

### Material Resources
- [ambientCG - Free PBR Textures](https://ambientcg.com/)
- [Poly Haven - Asset Library](https://polyhaven.com/)
- [Textures.com - Professional](https://www.textures.com/)

---

## 📱 Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome/Edge | ✅ Full | WebGL 2 required |
| Firefox | ✅ Full | WebGL 2 required |
| Safari | ⚠️ Partial | May need WebGL fallback |
| Mobile | ⚠️ Limited | Touch controls needed |

---

## 🔐 Performance Tips

1. **Reduce Segment Count** if experiencing lag:
   ```javascript
   <sphereGeometry args={[1.5, 32, 32]} />  // Instead of 64x64
   ```

2. **Disable Shadows** if needed:
   ```javascript
   directionalLight.castShadow = false;
   ```

3. **Use Stats Monitor**:
   ```javascript
   import Stats from 'three/examples/jsm/libs/stats.module.js';
   // Monitor FPS and memory usage
   ```

4. **Optimize Texture Size**:
   - Currently 512x512
   - Can reduce to 256x256 if needed
   - Increase to 1024x1024 for detail

---

## ✨ Tips & Tricks

1. **Best Material Comparison**
   - Set Roughness = 0, Metalness = 1
   - Makes material look like polished metal
   - Notice reflection differences clearly

2. **Dramatic Lighting**
   - Set Light Intensity = 5
   - Increase Roughness slightly
   - See how shadows enhance realism

3. **Learning Mode**
   - Adjust one slider at a time
   - Observe how changes affect appearance
   - Compare with basic material on right

---

## 📞 Support

For issues or questions:
1. Check the DOCUMENTATION.md file
2. Review the README.md in parent folder
3. Check Three.js/Drei documentation
4. Consult browser console for errors

---

**Last Updated:** March 28, 2026  
**Version:** 1.0  
**Status:** Ready to Use ✅
