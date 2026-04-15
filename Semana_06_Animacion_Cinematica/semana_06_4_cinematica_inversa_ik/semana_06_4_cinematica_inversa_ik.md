
# Taller - Cinemática Inversa: Haciendo que el Modelo Persiga Objetivos

## Objetivo del taller

Aplicar cinemática inversa (**IK, Inverse Kinematics**) para que un modelo 3D alcance un punto objetivo dinámico, como una mano intentando tocar una esfera. Este ejercicio permite comprender cómo una cadena de articulaciones puede ajustarse automáticamente para alcanzar una posición deseada usando algoritmos como CCD o FABRIK.

---

## Actividades por entorno

Este taller puede desarrollarse en **Unity** o **Three.js con React Three Fiber**, con énfasis en la implementación **paso a paso de un solver IK básico**.

---

### Unity (versión LTS) – Ejemplo detallado

**Requisitos iniciales:**

- Crear una jerarquía de `GameObjects` en el editor con 3 a 4 segmentos (por ejemplo: `Base → Brazo → Antebrazo → Mano`).
- Cada segmento debe estar unido como hijo del anterior y tener un `Transform` orientado en el eje positivo (e.g. +Z o +Y).

**Paso a paso:**

1. Crear un `GameObject` esférico que será el **objetivo** (por ejemplo, una `Sphere`).
2. Crear un script C# llamado `IKSolverCCD.cs`.
3. En el script:
 - Referenciar cada `Transform` de la cadena (del último al primero).
 - En cada `Update()`, aplicar el algoritmo **CCD (Cyclic Coordinate Descent)** para:
 - Rotar cada segmento de forma incremental hasta acercar la punta al objetivo.
 - Limitar la cantidad de iteraciones por frame.
4. Mover el objetivo manualmente con teclado, mouse o sliders en UI.
5. Visualizar la trayectoria o dirección del último eslabón con `Debug.DrawLine()` o una línea visible.
6. *Opcional:* Mostrar en la pantalla si el objetivo está fuera del alcance del brazo (por distancia máxima).

**Bonus:** Agregar un botón de "Reset Pose" y una interfaz para cambiar dinámicamente la cantidad de segmentos o el largo de cada uno.

---

### Three.js con React Three Fiber – Ejemplo detallado

**Requisitos iniciales:**

- Crear una escena con:
 - Un plano de fondo.
 - Una serie de `<mesh>` tipo `boxGeometry` para los eslabones del brazo.
 - Un `<mesh>` esfera como **objetivo** arrastrable con el mouse (usando `PointerDragControls` o manualmente con `leva`).

**Paso a paso:**

1. Crear un arreglo de `refs` para cada segmento.
2. Posicionar los segmentos uno tras otro dentro de `<group>`s jerárquicos.
3. En cada `useFrame()`:
 - Calcular el vector desde el extremo del brazo hacia el objetivo.
 - Implementar un solver **CCD o FABRIK** en JavaScript:
 - CCD: Para cada segmento desde el extremo hacia la base, calcular el ángulo necesario para acercar la punta al objetivo, y rotar el `group` correspondiente.
 - FABRIK: Usar la técnica de desplazamiento adelante-atrás para ajustar posiciones.
4. Mostrar una línea (`<Line>`) desde la base hasta el objetivo.
5. *Bonus:* Visualizar en pantalla la distancia restante y el número de iteraciones por frame.

**Opcional adicional:**
- Cambiar de IK a FK (Forward Kinematics) con un interruptor de estado.
- Añadir animaciones que permitan alternar entre poses predefinidas.

---

## Entrega

Crear carpeta con el nombre: `semana_6_4_cinematica_inversa_ik` en tu repositorio de GitLab.

Dentro de la carpeta, crear la siguiente estructura:

```
semana_6_4_cinematica_inversa_ik/
├── unity/
├── threejs/
├── media/ # Imágenes, videos, GIFs de resultados
└── README.md
```

### Requisitos del README.md

El archivo `README.md` debe contener obligatoriamente:

1. **Título del taller**: Taller Cinematica Inversa Ik
2. **Nombre del estudiante**
3. **Fecha de entrega**
4. **Descripción breve**: Explicación del objetivo y lo desarrollado
5. **Implementaciones**: Descripción de cada implementación realizada por entorno
6. **Resultados visuales**: 
 - **Imágenes, videos o GIFs** que muestren el funcionamiento
 - Deben estar en la carpeta `media/` y referenciados en el README
 - Mínimo 2 capturas/GIFs por implementación
7. **Código relevante**: Snippets importantes o enlaces al código
8. **Prompts utilizados**: Descripción de prompts usados (si aplicaron IA generativa)
9. **Aprendizajes y dificultades**: Reflexión personal sobre el proceso

### Estructura de carpetas

- Cada entorno de desarrollo debe tener su propia subcarpeta (`python/`, `unity/`, `threejs/`, etc.)
- La carpeta `media/` debe contener todos los recursos visuales (imágenes, GIFs, videos)
- Nombres de archivos en minúsculas, sin espacios (usar guiones bajos o guiones medios)

---

## Criterios de evaluación

- Cumplimiento de los objetivos del taller
- Código limpio, comentado y bien estructurado
- README.md completo con toda la información requerida
- Evidencias visuales claras (imágenes/GIFs/videos en carpeta `media/`)
- Repositorio organizado siguiendo la estructura especificada
- Commits descriptivos en inglés
- Nombre de carpeta correcto: `semana_6_4_cinematica_inversa_ik`
