# Three.js - Taller Proyecciones Camara Virtual

Implementacion completamente nueva en React + Vite + React Three Fiber para comparar:
- proyeccion en perspectiva
- proyeccion ortografica
- transformacion de un punto 3D a 2D en pantalla

## Integrantes
- Juan David Buitrago Salazar
- Juan David Cardenas Galvis
- Jeronimo Bermudez Hernandez
- Nelson Ivan Castellanos Betancourt
- Juan Pablo Correa Sierra
- Juan Felipe Fajardo Garzón

## Requisitos
- Node.js 18 o superior
- npm 9 o superior

## Instalacion y ejecucion
```bash
npm install
npm run dev
```

Build de produccion:
```bash
npm run build
npm run preview
```

## Funcionalidades implementadas
- Escena 3D con objetos distribuidos en distintas profundidades (eje Z).
- Alternancia entre `PerspectiveCamera` y `OrthographicCamera`.
- `OrbitControls` para manipular la vista en tiempo real.
- Panel overlay con:
  - tipo de camara activa
  - `fov`, `aspect`, `near`, `far`
  - `left`, `right`, `top`, `bottom`
- Bonus:
  - proyeccion de un punto fijo usando `Vector3.project(camera)`
  - lectura de coordenadas mundo, NDC y pixel.

## Estructura interna
```text
threejs/
├── src/
│   ├── components/
│   │   ├── CameraSystem.jsx
│   │   ├── OverlayPanel.jsx
│   │   └── SceneObjects.jsx
│   ├── constants/
│   │   ├── cameraConfig.js
│   │   └── sceneConfig.js
│   ├── App.jsx
│   ├── main.jsx
│   └── styles.css
├── index.html
├── package.json
└── vite.config.js
```

## Contribuciones del grupo

- **Juan David Buitrago Salazar:** Coordinación técnica del entregable, integración final y soporte en implementación.
- **Juan David Cardenas Galvis:** Desarrollo de componentes matemáticos y validación de resultados.
- **Jeronimo Bermudez Hernandez:** Implementación de funcionalidades y apoyo en integración.
- **Nelson Ivan Castellanos Betancourt:** Desarrollo de visualización y pruebas de comportamiento.
- **Juan Pablo Correa Sierra:** Implementación de componentes pendientes y soporte de integración.
- **Juan Felipe Fajardo Garzón:** Documentación de resultados y elaboración de evidencias.
