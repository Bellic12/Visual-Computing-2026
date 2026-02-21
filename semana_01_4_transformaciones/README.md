# Taller 4 - Transformaciones Básicas en Computación Visual

## Nombre del estudiante

Juan David Buitrago Salazar

## Fecha de entrega

`2026-02-21`

---

## Descripción breve

En este taller se implementaron transformaciones geométricas en distintos entornos para reforzar el uso de traslación, rotación y escala, tanto en 2D como en 3D. El objetivo principal fue comprender cómo estas transformaciones pueden representarse con matrices homogéneas y cómo su composición modifica una geometría base en el tiempo.

En Python se trabajó con una figura 2D (cuadrado en coordenadas homogéneas) para aplicar transformaciones individuales y una transformación compuesta. Además, se generó una animación temporal de 72 frames para observar la evolución de la matriz compuesta $M(t)$.

En Processing y Three.js se extendió el ejercicio al espacio 3D con animaciones en tiempo real, incluyendo órbitas, rotaciones por frame y variaciones de escala, lo que permitió comparar enfoques entre entornos de visualización interactiva.

---

## Implementaciones

### Python

Se desarrolló un notebook (`python/transformaciones_2D.ipynb`) con:

- Construcción de un cuadrado base en coordenadas homogéneas (matriz $3\times N$).
- Definición de matrices homogéneas de traslación, rotación y escala (3×3).
- Aplicación de transformaciones estáticas individuales y compuestas ($M=T\cdot R\cdot S$).
- Generación de animación temporal con 72 frames y exportación a GIF.
- Registro e impresión de muestras de la matriz compuesta $M(t)$ para distintos valores de tiempo.

### Three.js / React Three Fiber

En `threejs/` se implementó una escena 3D con React Three Fiber y Drei:

- Cubo animado con traslación orbital en $x,y,z$.
- Rotación incremental por frame en los tres ejes.
- Escala pulsante con función sinusoidal.
- Trail/orbita visual con línea discontinua, grid y fondo estelar.
- Panel HUD con telemetría en tiempo real (posición, rotación, escala y tiempo).

### Processing

En `proccesing/transformaciones_basicas.pde` se implementó una escena P3D con:

- Cubo principal con traslación oscilatoria, rotaciones múltiples y escala pulsante.
- Cubo satélite en órbita con rotación propia.
- HUD con variables dinámicas (`millis`, `frameCount`, desplazamiento y escala).

---

## Resultados visuales

### Python - Implementación

![Geometría inicial en Python](./media/python_geometria_inicial.png)

Visualización de la figura base (cuadrado en coordenadas homogéneas) antes de aplicar transformaciones.

![Transformaciones estáticas en Python](./media/python_transformaciones.png)

Comparación de traslación, rotación, escala y transformación compuesta sobre la geometría original.

![Animación temporal Python](./media/python.gif)

Animación de 72 frames donde la transformación compuesta evoluciona en el tiempo y modifica posición, orientación y tamaño de la figura.

### Processing - Implementación

![Animación de Processing](./media/proccesing.gif)

Escena 3D con cubo principal y cubo satélite, mostrando traslación, rotación y escala con comportamiento temporal.

### Three.js - Implementación

![Animación de Three.js](./media/threejs.gif)

Escena interactiva en navegador con trayectoria orbital 3D, rotación continua y HUD de telemetría.

---

## Matriz compuesta en el tiempo

Durante la animación en Python se generaron **72 frames** y se registraron muestras de la matriz compuesta $M(t)$:

Frame 01 (t=0.00)

```text
[[0.5 0.  2. ]
 [0.  0.5 0. ]
 [0.  0.  1. ]]
```

Frame 19 (t=0.25)

```text
[[ 0. -1.  0.]
 [ 1.  0.  2.]
 [ 0.  0.  1.]]
```

Frame 37 (t=0.50)

```text
[[-1.5 -0.  -2. ]
 [ 0.  -1.5  0. ]
 [ 0.   0.   1. ]]
```

Frame 55 (t=0.75)

```text
[[-0.  1. -0.]
 [-1. -0. -2.]
 [ 0.  0.  1.]]
```

Frame 72 (t=0.99)

```text
[[ 0.5    0.044  1.992]
 [-0.044  0.5   -0.174]
 [ 0.     0.     1.   ]]
```

Estas muestras muestran cómo la composición $M(t)=T(t)\cdot R(t)\cdot S(t)$ cambia de forma continua y periódica a lo largo de la animación.

---

## Código relevante

### Python — Composición de transformaciones y registro de matriz temporal

```python
affine_t = shift_matrix(dx_t, dy_t) @ spin_matrix(ang_t) @ resize_matrix(scl_t, scl_t)
shape_t = run_affine(affine_t, shape0)
matrix_log.append((frame_idx, tau, affine_t))
```

Este extracto es el núcleo matemático de la animación 2D: compone la matriz homogénea $M(t)=T(t)\cdot R(t)\cdot S(t)$, la aplica sobre la figura base y guarda cada matriz para analizar cómo cambia con el tiempo.

### Processing — Transformación dinámica del cubo principal

```java
float vaivenX = sin(tiempo) * 150;
float vaivenY = cos(tiempo) * 80;
translate(vaivenX, vaivenY, 0);

rotateX(frameCount * 0.01);
rotateY(frameCount * 0.02);
rotateZ(frameCount * 0.005);

float escalaActual = pulsoEscala();
scale(escalaActual);
```

Este extracto controla la animación 3D en Processing: primero desplaza el cubo en una trayectoria oscilatoria, luego aplica rotaciones en los tres ejes y finalmente modula su tamaño con un pulso sinusoidal.

### Three.js — Telemetría de traslación, rotación y escala por frame

```javascript
const movementX = Math.cos(t * 0.8) * PATH_SETTINGS.orbitSize
const movementY = Math.sin(t * 0.8) * PATH_SETTINGS.orbitSize
const movementZ = Math.sin(t * 1.2) * PATH_SETTINGS.depthSwing
solid.position.set(movementX, movementY, movementZ)

solid.rotation.x += SPIN_STEPS.x
solid.rotation.y += SPIN_STEPS.y
solid.rotation.z += SPIN_STEPS.z

const smoothScale = 1 + 0.4 * Math.sin(t * 2)
solid.scale.setScalar(smoothScale)
```

Este extracto define la actualización por frame en React Three Fiber: calcula la posición orbital en 3D, acumula rotación incremental y aplica escala pulsante para producir una transformación continua y medible en el HUD.

---

## Prompts utilizados

### Prompt 1 — Entorno Python (Notebook de transformaciones 2D)

```text
Actúa como experto en computación visual y genera un notebook de Python para explicar transformaciones geométricas 2D con matrices homogéneas 3x3.

Requisitos técnicos:
- Usar numpy, matplotlib e imageio.
- Crear un cuadrado unitario centrado en el origen en formato homogéneo (matriz 3xN).
- Implementar funciones: shift_matrix(dx,dy), spin_matrix(theta), resize_matrix(sx,sy), run_affine(M,P).
- Mostrar transformaciones estáticas (traslación, rotación, escala y compuesta T·R·S) en subplots comparando contra la figura original.
- Generar animación temporal de 72 frames con parámetros:
	dx(t)=2*cos(2*pi*t), dy(t)=2*sin(2*pi*t), theta(t)=2*pi*t, s(t)=0.5+sin(pi*t)^2.
- Imprimir muestras de M(t) en frames 1, 19, 37, 55 y 72.
- Exportar GIF final a media/python.gif (o fallback local si no hay permisos).

Además, documenta cada bloque en markdown y explica por qué el orden T·R·S cambia el resultado.
```

### Prompt 2 — Entorno Three.js (React + R3F + Drei)

```text
Quiero una app Vite con React y React Three Fiber que muestre una escena 3D educativa de transformaciones.

Implementa:
- Un cubo principal con animación por frame usando useFrame.
- Traslación orbital en x,y,z con funciones seno/coseno.
- Rotación incremental en los tres ejes.
- Escala pulsante con sin(t).
- Un trail/orbita visual (Line), un Grid en el piso, estrellas de fondo y OrbitControls.
- Un HUD en HTML/CSS que muestre telemetría en tiempo real: posición, rotación, escala y tiempo.

Arquitectura esperada:
- Componente AnimatedSolid para la lógica de transformación.
- Componente SceneRig para luces y ayudas visuales.
- Componente HeadUpDisplay para métricas.
- Estados y callbacks limpios con useState/useCallback.

Entrega el código completo de App.jsx y estilos básicos de App.css con diseño legible.
```

### Prompt 3 — Entorno Processing (P3D)

```text
Genera un sketch de Processing (Java mode, P3D) para demostrar transformaciones 3D en tiempo real.

Debe incluir:
- Canvas 800x600 y fondo oscuro.
- Cubo principal con traslación oscilatoria (sin/cos), rotación en X/Y/Z y escala pulsante.
- Cubo satélite orbitando alrededor del principal con rotación propia y escala reducida.
- HUD de texto en pantalla con millis(), frameCount, desplazamiento en X y escala actual.
- Organización del código con funciones separadas: dibujarCuboPrincipal(), dibujarCuboSatelite(), dibujarHUD().

Quiero código limpio, variables descriptivas en español y una animación estable para grabar un GIF demostrativo.
```

---

## Aprendizajes y dificultades

### Aprendizajes

Se reforzó el uso de coordenadas homogéneas como marco unificado para aplicar traslación, rotación y escala mediante multiplicación matricial. También quedó más claro que el orden de composición de matrices afecta directamente el resultado geométrico.

A nivel práctico, se consolidó la relación entre representación matemática y resultado visual, comparando una implementación analítica en Python con visualizaciones en tiempo real en Processing y Three.js.

### Dificultades

Una dificultad importante fue coordinar parámetros temporales para lograr animaciones estables y legibles (velocidad de giro, rango de escala y amplitud de traslación), evitando movimientos excesivos o pérdida de referencia espacial.

También fue retador mantener consistencia entre entornos (2D vs 3D) para que las mismas ideas de transformación se entendieran de forma equivalente en distintas herramientas.

### Mejoras futuras

Como siguiente paso, se puede incluir una visualización explícita de ejes locales/globales y descomposición de matrices por frame para depuración didáctica. También sería útil incorporar controles interactivos para modificar parámetros en tiempo real y observar cómo cambia $M(t)$ inmediatamente.

---

## Contribuciones grupales

Taller realizado de forma individual.

---

## Estructura del proyecto

```text
semana_01_4_transformaciones/
├── python/
│   ├── transformaciones_2D.ipynb   # Notebook principal (matrices y animación)
│   ├── output/                      # Salidas auxiliares (fallbacks / exportaciones)
│   └── .venv/                       # Entorno virtual local de Python
├── threejs/
│   ├── package.json                 # Dependencias y scripts de Vite
│   ├── index.html                   # Punto de entrada HTML
│   ├── vite.config.js               # Configuración de Vite
│   ├── eslint.config.js             # Configuración de lint
│   └── src/
│       ├── App.jsx                  # Escena 3D y lógica de animación
│       ├── App.css                  # Estilos del HUD/interfaz
│       ├── main.jsx                 # Bootstrap de React
│       ├── index.css                # Estilos globales
│       └── assets/                  # Recursos estáticos del frontend
├── proccesing/
│   └── transformaciones_basicas.pde # Sketch P3D con dos cubos y HUD
├── media/
│   ├── python.gif
│   ├── python_geometria_inicial.png
│   ├── python_transformaciones.png
│   ├── proccesing.gif
│   └── threejs.gif
├── 04_plantilla_readme_entregas_talleres.md
└── README.md
```

---

## Referencias

- Documentación oficial de NumPy: https://numpy.org/doc/
- Documentación oficial de Matplotlib: https://matplotlib.org/stable/
- Documentación oficial de Processing: https://processing.org/reference/
- React Three Fiber Docs: https://docs.pmnd.rs/react-three-fiber/
- Drei Docs: https://github.com/pmndrs/drei
- Three.js Docs: https://threejs.org/docs/

---

## Checklist de entrega

- [x] Carpeta con nombre `semana_01_4_transformaciones`
- [x] Código limpio y funcional en carpetas por entorno
- [x] GIFs/imágenes incluidos con nombres descriptivos en carpeta `media/`
- [x] README completo con todas las secciones requeridas
- [x] Mínimo 2 capturas/GIFs en la implementación de Python
- [x] Commits descriptivos en inglés
- [x] Repositorio organizado y público

---
