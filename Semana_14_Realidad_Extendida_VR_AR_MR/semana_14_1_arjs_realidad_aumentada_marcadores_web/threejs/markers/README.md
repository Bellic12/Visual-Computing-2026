# Marcadores Barcode (matriz 3×3)

La app usa **marcadores barcode**: rejillas negro/blanco de alto contraste que se
detectan mucho mejor que los patrones clásicos Hiro/Kanji (funcionan en pantalla, a
distancia y con luz no ideal). Configuración en `../index.html`:
`detectionMode: mono_and_matrix; matrixCodeType: 3x3`.

| Marcador (`value`) | Modelo que proyecta | Imagen para mostrar/imprimir |
|--------------------|---------------------|------------------------------|
| **1** | Astronauta 3D (glTF) animado | [`marcador-1-astronauta.png`](marcador-1-astronauta.png) |
| **2** | "Sistema solar" de primitivas | [`marcador-2-sistema-solar.png`](marcador-2-sistema-solar.png) |
| **5** | Caja roja giratoria | [`marcador-5-caja.png`](marcador-5-caja.png) |

Cada imagen lleva un margen blanco amplio (*quiet zone*), imprescindible para que la
cámara reconozca el marcador.

## Cómo mostrarlos a la cámara

Montaje recomendado (sin impresora ni segundo monitor): **corre la app en el celular y
muestra el marcador en la pantalla del PC.**

1. En el PC abre el marcador, p. ej. `marcador-1-astronauta.png`, a pantalla completa.
2. En el celular abre la app por **HTTPS** (la cámara exige contexto seguro) y apunta la
   cámara trasera a la pantalla del PC.

Recomendaciones: marcador **plano y de frente**, con **blanco visible por los 4 lados**,
brillo de pantalla moderado (evitar reflejos) y buena luz ambiente.
