import React, { useRef, useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { PerspectiveCamera, OrbitControls, Grid } from '@react-three/drei';
import * as THREE from 'three';
import GUI from 'lil-gui';
import PBRMaterialScene from './components/PBRMaterialScene';
import './App.css';

function App() {
  const sceneRef = useRef(null);

  return (
    <div className="app-container">
      <header className="header">
        <h1>PBR Materials Workshop - Three.js</h1>
        <p>Explore physically-based rendering with interactive material controls</p>
      </header>
      
      <div className="canvas-container">
        <Canvas ref={sceneRef} gl={{ antialias: true, alpha: true }}>
          <PerspectiveCamera makeDefault position={[5, 5, 8]} />
          <OrbitControls />
          <PBRMaterialScene />
        </Canvas>
      </div>

      <aside className="info-panel">
        <h3>PBR Material Controls</h3>
        <p className="info-text">
          Three different PBR texture sets with interactive controls:
        </p>
        <ul>
          <li><strong>Left (Sphere):</strong> Bricks092 texture</li>
          <li><strong>Center (Cube):</strong> Metal034 texture</li>
          <li><strong>Right (Cylinder):</strong> Metal049A texture</li>
        </ul>
        <p className="info-text small">
          <strong>Controls:</strong> Adjust roughness, metalness, and light intensity to see how materials respond
        </p>
      </aside>
    </div>
  );
}

export default App;
