# Espacios Proyectivos y Matrices de Proyección - Three.js

Este proyecto demuestra la diferencia entre cámaras perspectivas y ortográficas en Three.js usando React Three Fiber, mostrando cómo cambia la percepción de profundidad con cada tipo de proyección.

## Características

- Escena con 3 objetos posicionados a diferentes profundidades
- Cambio dinámico entre cámara perspectiva y ortográfica
- OrbitControls para navegación libre alrededor de los objetos
- Visualización clara de cómo cambia la percepción de profundidad
- Grid de referencia y líneas de profundidad
- Interfaz intuitiva con botones de control

## Objetos en la escena

- Cubo Rojo: Posicionado cerca (z = 0)
- Esfera Azul: Posicionado a media distancia (z = -5)
- Cono Verde: Posicionado lejos (z = -10)

## Diferencias entre proyecciones

**Cámara Perspectiva:**
- Simula la visión humana
- Los objetos lejanos se ven más pequeños
- Líneas paralelas convergen en puntos de fuga
- Proporciona sensación de profundidad realista

**Cámara Ortográfica:**
- Proyección paralela sin punto de fuga
- Todos los objetos mantienen su tamaño relativo sin importar la distancia
- Las líneas paralelas permanecen paralelas
- Útil para diseño técnico y arquitectónico

## Instalación

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

El proyecto se abrirá en `http://localhost:5173`

## Uso

1. Observa la escena inicial con la cámara perspectiva
2. Usa los botones en la parte inferior para cambiar entre tipos de cámara
3. Nota cómo los tres objetos parecen cambiar de tamaño al cambiar de cámara
4. Usa el mouse para rotar la cámara (OrbitControls):
   - Click izquierdo + arrastrar: Rotar
   - Scroll: Zoom
   - Click derecho + arrastrar: Pan
5. Observa las líneas de referencia que marcan la profundidad de cada objeto

## Conceptos demostrados

- Matriz de proyección perspectiva: Crea profundidad mediante la división por perspectiva
- Matriz de proyección ortográfica: Mantiene proporciones sin efecto de profundidad
- Espacio de vista (View Space): Transformación de coordenadas del mundo a coordenadas de cámara
- Espacio de clip (Clip Space): Resultado de aplicar la matriz de proyección

## Tecnologías

- React 18
- Vite
- Three.js
- React Three Fiber
- @react-three/drei (OrbitControls, PerspectiveCamera, OrthographicCamera, Grid)

## Estructura del proyecto

```
src/
  ├── App.jsx              # Componente principal con controles
  ├── App.css              # Estilos de la aplicación
  ├── main.jsx             # Punto de entrada
  ├── index.css            # Estilos globales
  └── components/
      └── DepthScene.jsx   # Escena 3D con objetos y cámaras
```
