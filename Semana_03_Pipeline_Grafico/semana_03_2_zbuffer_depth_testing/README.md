# Taller - Proyecciones 3D: Cómo ve una Cámara Virtual

## Integrantes

- Juan David Buitrago Salazar
- Juan David Cardenas Galvis
- Nicolás Rodríguez Piraban
- Camilo Andres Medina Sanchez
- Juan Felipe Fajardo Garzón

**Fecha de entrega:**  09/03/2026

## Descripción breve

## Implementaciones

### Python

### Unity

### Three.js

Se implementó una escena 3D básica con una cámara de tipo PerspectiveCamara.
Se añadieron 5 cubos en diferentes posiciones en el eje Z para observar cómo
el pipeline de renderizado determina qué fragmentos son visibles.

## Resultados visuales

### Python

### Unity

![far plane shader](media/far_plane_shader.gif)

![z_fighting_unity](media/z_fighting_unity.gif)

![buffer_comparation](media/buffer_comparation.gif)

### Three.js

![Resultado Threejs 1](./media/threejs_png_1.png)

Esta imágen muestra la escena 3D creada. La escena está compuesta por 5 cubos de
diferentes colores y un sistema de ejes como referencia.

![Resultado Threejs 2](./media/threejs_gif_1.gif)

Este GIF muestra como, al desactivar el Z-Buffer, la visualización de los objetos
cambia, mostrando como se dibujan los objetos en el orden en que se establece en
el código, dibujando elementos que no se deberían ver al estar detras de otros.

## Código relevante

### Python

### Unity

### Three.js

```js
const depthMaterial = new THREE.ShaderMaterial({
  vertexShader: `
    void main() {
      gl_Position = projectionMatrix *
                    modelViewMatrix *
                    vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    void main() {
      float depth = gl_FragCoord.z;
      depth = pow(depth, 20.0); // exagera diferencias
      vec3 color = vec3(1.0, 0.4, 0.2);
      gl_FragColor = vec4(color * depth, 1.0);
    }
  `,
  depthTest: true,
  depthWrite: true
});
```

Este fragmento de código es el que se encarga de crear el depth material para aplicarlo
a los objetos de la escena.

## Aprendizajes y dificultades

## Contribuciones del grupo
