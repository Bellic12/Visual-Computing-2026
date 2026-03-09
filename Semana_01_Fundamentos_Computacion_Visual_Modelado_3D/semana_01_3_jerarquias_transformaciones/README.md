# Taller 3 — Jerarquías y Transformaciones: El Árbol del Movimiento

## Nombre del estudiante

Juan David Buitrago Salazar

## Fecha de entrega

`2026-02-21`

---

## Descripción breve

En este taller se trabajó el concepto de jerarquías de transformación en gráficos 3D, aplicando transformaciones locales y globales sobre nodos padre-hijo. El objetivo fue construir y controlar estructuras jerárquicas en tiempo real para verificar cómo los hijos heredan los cambios del nodo padre.

La implementación se desarrolló en dos entornos: **Three.js con React Three Fiber** y **Unity LTS**. En ambos casos se construyeron jerarquías de al menos tres niveles y se controlaron transformaciones del nodo padre desde interfaz (Leva en Three.js y sliders UI en Unity), incluyendo animación con pausa/reinicio como parte del bonus.

---

## Implementaciones

### Unity

Se implementó una escena base con un controlador `ControladorJerarquia.cs` que permite modificar el transform del objeto padre desde UI (sliders de posición, rotación y escala), alternar animación continua y reiniciar estado inicial.

Adicionalmente, el script fue refinado con helpers para lectura de vectores y sincronización de sliders de rotación durante la animación, mejorando claridad y mantenimiento del código.

Estado actual: **completado** para esta entrega.

### Three.js / React Three Fiber

Se creó un proyecto con Vite + React Three Fiber con una estructura jerárquica usando `group` y múltiples objetos 3D. Sobre el nodo padre se aplicaron transformaciones de traslación y rotación para observar, en tiempo real, cómo se comportan los nodos hijos.

El control interactivo se resolvió con `leva`, permitiendo ajustar con sliders los parámetros del nodo padre. Como bonus, se incluyó un tercer nivel en la jerarquía para visualizar transformaciones encadenadas.

---

## Resultados visuales

### Three.js - Implementación

![Jerarquía con referencia global/local](./media/threejs_orbitas_posicion_global_local.gif)

Se observa la estructura padre-hijo-nieto y cómo la transformación local de cada objeto se ve afectada por las transformaciones aplicadas al nodo padre.

![Transformaciones desde nodo padre](./media/threejs_transformaciones_nodo_padre.gif)

Se evidencia que al transformar el nodo raíz (traslación/rotación), todo el sistema jerárquico se desplaza y reorienta de manera coherente.

### Unity - Implementación

![Jerarquía con rotación por niveles](./media/unity_jerarquia.gif)

Este GIF muestra la jerarquía haciendo rotación en cada uno de los elementos y permite observar cómo cada transformación afecta a sus hijos por composición padre-hijo.

![Interfaz y transformaciones del sistema completo](./media/unity_transformaciones.gif)

Este GIF muestra la animación con la interfaz de control (sliders y botones) y las transformaciones posibles aplicadas sobre todo el sistema jerárquico.

---

## Código relevante

### Three.js (React Three Fiber) — Jerarquía padre-hijo con transformaciones encadenadas

### Three.js (React Three Fiber) — Composición jerárquica explícita

```jsx
<group rotation={[rotX, rotY, rotZ]} position={[trX, trY, trZ]}>
  <RotatingBody source={MODEL_FILES.sun} scale={sun} spinRate={0.25} />

  <OrbitNode orbitSpeed={earthOrbit} radius={sun * 10 + 40} startAngle={Math.PI * 0.3}>
    <RotatingBody source={MODEL_FILES.earth} scale={earth} spinRate={0.5} />

    <OrbitNode orbitSpeed={moonOrbit} radius={12}>
      <RotatingBody source={MODEL_FILES.moon} scale={moon} />
    </OrbitNode>
  </OrbitNode>
</group>
```

Este bloque muestra la **jerarquía padre-hijo-nieto**. El grupo raíz recibe traslación y rotación, y los niveles internos heredan automáticamente esos cambios, evidenciando el comportamiento jerárquico pedido en el taller.

### Unity (C#) — Control del transform del padre desde UI

```csharp
void AplicarSliders()
{
  padre.position   = LeerVector3(sliderPosX, sliderPosY, sliderPosZ);
  padre.rotation   = Quaternion.Euler(LeerVector3(sliderRotX, sliderRotY, sliderRotZ));
  padre.localScale = LeerVector3(sliderEscX, sliderEscY, sliderEscZ);
}

void EjecutarAnimacion()
{
  float delta = VelocidadRotacion * Time.deltaTime;
  padre.Rotate(delta, delta, delta);

  SincronizarSliderRotacion();
}

static Vector3 LeerVector3(Slider x, Slider y, Slider z)
  => new Vector3(x.value, y.value, z.value);
```

Este extracto concentra la lógica principal de Unity: aplicar transformaciones del padre desde UI y, en modo animación, mantener sincronizados los sliders con la rotación real del objeto para evitar desalineaciones visuales.

---

## Prompts utilizados

### Prompt para replicar entorno Three.js / React Three Fiber

```text
Actúa como desarrollador senior de React Three Fiber. Crea un proyecto Vite + React con una jerarquía 3D usando <group> y varios <mesh> en relación padre → hijo → nieto. Requisitos: 1) aplicar traslación y rotación al nodo padre, 2) demostrar visualmente que los hijos heredan transformaciones, 3) usar Leva (o dat.GUI) para sliders de posición y rotación del padre en tiempo real, 4) incluir iluminación y cámara con OrbitControls, 5) organizar el código en componentes claros y explicar brevemente cómo se aplica la jerarquía.
```

### Prompt para replicar entorno Unity

```text
Actúa como desarrollador Unity (C#) para un taller de jerarquías de transformaciones en Unity LTS. Necesito una escena 3D con al menos 3 objetos anidados (padre → hijo → nieto). Crea un script MonoBehaviour para controlar posición, rotación y escala del padre usando sliders UI; añade botones para animar, pausar y reiniciar; y muestra en TMP los valores actuales de posición, rotación y escala. Entrega también instrucciones de configuración de Canvas/UI y asignación de referencias en el Inspector.
```

---

## Aprendizajes y dificultades

### Aprendizajes

Se reforzó la diferencia entre transformaciones **locales** y **globales**, y cómo una modificación en el nodo padre impacta directamente toda la cadena de hijos y nietos.

A nivel de herramientas, se consolidó el uso de React Three Fiber para abstraer escenas complejas por componentes reutilizables y el uso de Leva para inspección interactiva de parámetros de transformación.

### Dificultades

La principal dificultad fue mantener un comportamiento consistente entre controles de UI y transformaciones jerárquicas, especialmente al alternar entre control manual y animación.

En Unity, el mayor reto fue coordinar de forma consistente UI, animación y estado del transform sin duplicar lógica; se resolvió separando funciones (`AplicarSliders`, `EjecutarAnimacion`, helpers) y sincronizando explícitamente sliders/rotación.

### Mejoras futuras

- Añadir ejes locales/globales visibles para depurar orientación.
- Sincronizar mejor unidades y escalas entre Unity y Three.js para comparar resultados de forma más directa.

---

## Contribuciones grupales (si aplica)

Taller realizado de forma individual.

---

## Estructura del proyecto

```text
semana_01_3_jerarquias_transformaciones/
├── 04_plantilla_readme_entregas_talleres.md
├── README.md
├── media/
│   ├── threejs_orbitas_posicion_global_local.gif
│   ├── threejs_transformaciones_nodo_padre.gif
│   ├── unity_jerarquia.gif
│   └── unity_transformaciones.gif
├── threejs/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── eslint.config.js
│   ├── public/
│   │   └── models/
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── main.jsx
│       ├── index.css
│       └── assets/
└── unity/
    └── solar_system/
        ├── Assets/
        │   ├── ControladorJerarquia.cs
        │   ├── InputSystem_Actions.inputactions
        │   ├── MaterialSol.mat
        │   ├── MaterialTierra.mat
        │   ├── Scenes/
        │   ├── Settings/
        │   ├── TextMesh Pro/
        │   └── TutorialInfo/
        ├── Packages/
        │   ├── manifest.json
        │   └── packages-lock.json
        └── ProjectSettings/
            ├── ProjectSettings.asset
            ├── ProjectVersion.txt
            └── EditorBuildSettings.asset
```

---

## Créditos de modelos y texturas

### Modelos 3D (Sketchfab)

- **Low Poly Planet Earth**
  - Autor: **Jacobs Development**
  - Triangles: **9.2k** | Vertices: **4.6k**
  - Descripción: planeta Tierra low poly.
  - Licencia: **CC Attribution (Creative Commons Attribution)**
  - Enlace: https://sketchfab.com/3d-models/low-poly-planet-earth-7b1dc4f802a54a6297e7a46888a85f77

- **Low Poly Moon**
  - Autor: **FoxVenture**
  - Triangles: **1.7k** | Vertices: **1.3k**
  - Descripción: luna low poly simple.
  - Licencia: **CC Attribution (Creative Commons Attribution)**
  - Enlace: https://sketchfab.com/3d-models/low-poly-moon-d671eb35d2244c8cb98d06b4948d9937

- **Saturn (planet)**
  - Autor: **SebastianSosnowski**
  - Triangles: **8.8k** | Vertices: **4.5k**
  - Descripción: modelo de Saturno con posiciones de distancia para cinco lunas (Enceladus, Mimas, Tethys, Dione y Rhea).
  - Licencia: **CC Attribution (Creative Commons Attribution)**
  - Enlace: https://sketchfab.com/3d-models/saturn-planet-9ab1eb3bb97f4e4a9305c0aae2d280a6

- **PS1 style low poly Sun**
  - Autor: **albert_buscio**
  - Triangles: **960** | Vertices: **482**
  - Descripción: Sol low poly estilo PS1, texturizado y listo para integrar en proyectos low poly.
  - Licencia: **CC Attribution (Creative Commons Attribution)**
  - Enlace: https://sketchfab.com/3d-models/ps1-style-low-poly-sun-9f2b6f87811242b8b6313b42667122cf
  - Nota del autor: las texturas usadas en ese modelo provienen de https://www.solarsystemscope.com/textures/.

### Texturas (Unity)

- **Solar System Scope Textures**
  - Fuente: https://www.solarsystemscope.com/textures/
  - Uso: texturas empleadas para materiales planetarios en la implementación de Unity.

---

## Referencias

- Documentación React Three Fiber: https://docs.pmnd.rs/react-three-fiber
- Documentación Three.js: https://threejs.org/docs/
- Documentación `Object3D` en Three.js: https://threejs.org/docs/#api/en/core/Object3D
- Documentación Unity Transform: https://docs.unity3d.com/ScriptReference/Transform.html
- Documentación Unity UI Slider: https://docs.unity3d.com/Packages/com.unity.ugui@latest/index.html
- Modelos 3D (Sketchfab):
  - Low Poly Planet Earth: https://sketchfab.com/3d-models/low-poly-planet-earth-7b1dc4f802a54a6297e7a46888a85f77
  - Low Poly Moon: https://sketchfab.com/3d-models/low-poly-moon-d671eb35d2244c8cb98d06b4948d9937
  - Saturn (planet): https://sketchfab.com/3d-models/saturn-planet-9ab1eb3bb97f4e4a9305c0aae2d280a6
  - PS1 style low poly Sun: https://sketchfab.com/3d-models/ps1-style-low-poly-sun-9f2b6f87811242b8b6313b42667122cf
- Texturas de planetas: https://www.solarsystemscope.com/textures/

---

## Checklist de entrega

- [x] Carpeta con nombre `semana_01_3_jerarquias_transformaciones`
- [x] Código funcional en carpetas `threejs/` y `unity/`
- [x] README completo con secciones requeridas
- [x] Resultados visuales de Three.js incluidos en `media/`
- [x] Resultados visuales finales de Unity
- [x] Repositorio organizado por entorno
