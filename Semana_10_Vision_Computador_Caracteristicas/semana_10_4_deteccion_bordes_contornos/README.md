# Taller - Detección de Bordes y Contornos
## Nombre:

- Juan David Buitrago Salazar
- Juan David Cardenas Galvis
- Nicolás Rodríguez Piraban
- Camilo Andres Medina Sanchez
- Juan Felipe Fajardo Garzón

## Fecha de entrega: 18/05/2026

## Descripción breve:
Este taller implementó múltiples técnicas de detección de bordes y procesamiento de imágenes en Processing, incluyendo los operadores Sobel, filtros de convolución y efectos artísticos aplicados a los contornos detectados.

## Implementaciones:

### Processing:
Se desarrolló un sketch que aplica 16 efectos diferentes organizados en 4 filas: filtros básicos de detección de bordes (Sobel X, Y y magnitud), filtros de procesamiento (Edge Detection, Sharpen, Blur), efectos artísticos (Negativo, Sepia, Posterizar, Relieve) y bordes artísticos (Borde Invertido, Color Falso, Solarizado, Estilo Dibujo).

## Resultados visuales:

### Processing:

Se hizo uso de la siguiente imagen de prueba

![alt text](media/bike.jpg)

La aplicación muestra una grilla con 16 resultados diferentes. 

![alt text](media/complete_grid_bike.png)

Los operadores Sobel detectan cambios abruptos de intensidad en direcciones horizontales y verticales. Se puede evidenciar como en Sobel X no se detecta las lineas horizontales del fondo, puesto que este solo detecta cambios sobre el eje x, mientras que sobel Y no detecta la linea vertical del suelo por una razón similar (solo identifica cambiós sobre el eje Y)

Tambien se usa el detector de sobel por magnitud (combinación de X y Y), en esta imagen se observa una mejor detección de bordes en todas las direcciones

![alt text](media/sobel_bike.png)


En la segunda fila se realiza otro tipo de procesamientos a la imagen, el primero es un detector de bordes usando un kernel derivativo en todas las direcciones, en el segundo se usa un kernel que resalta ("afilamiento") los bordes, finalmente, en las últimas 2 columnas se realizar un efecto de suavizado o blur, tanto gaussiano como de promedio (también llamado box blur); en este último tipo de suavizado se hace uso de un kernel en el cual, al hacer la convolución, cada pixel toma el valor del promedio de sus vecinos

![alt text](media/miscellaneous_processing_bike.png)

Para la siguiente parte (aplicar filtros artísticos) se crearon métodos especiales, los cuales cambian los valores RGB de cada pixel en la imagen original, según el filtro a aplicar. Primero se aplciaron filtros Negativo y Sepia, luego se hizo una posterización (o reducción de la gama de colores), y finalmente se aplicó un filtro de alto relieve, similar a la detección de bordes presentada anteriormente

![alt text](media/color_filters_bike.png)

Finalmente se combinó la detección de bordes con los cambios de color para aplicar filtros "artísticos" a los bordes de la imagen. Los efectos de bordes artísticos aplican colores falsos basados en la dirección del gradiente o crean estilos visuales únicos como el efecto solarizado estilo Instagram.

![alt text](media/art_border_bike.png)

## Código relevante:

Inicialmente se definen los kernels que se van a utilizar más adelante para las operaciones de convolución

```java
// Kernels
float[][] kernelSobelX = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
float[][] kernelSobelY = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
float[][] kernelEdge = {{-1, -1, -1}, {-1, 8, -1}, {-1, -1, -1}};
float[][] kernelSharpen = {{0, -1, 0}, {-1, 5, -1}, {0, -1, 0}};
float[][] kernelBlur = {{1/9.0, 1/9.0, 1/9.0}, {1/9.0, 1/9.0, 1/9.0}, {1/9.0, 1/9.0, 1/9.0}};
float[][] kernelGauss = {{1/16.0, 2/16.0, 1/16.0}, {2/16.0, 4/16.0, 2/16.0}, {1/16.0, 2/16.0, 1/16.0}};
float[][] kernelEmboss = {{-2, -1, 0}, {-1, 1, 1}, {0, 1, 2}};
```

Luego se crea el método convolver para aplicar convoluciones, esto se hace con el objetivo de facilitar las operaciones, si se desea cambiar el tipo de procesamiento solo es necesario usar otro kernel en vez de modificar todo el algorítmo

```java
PImage convolver(PImage origen, float[][] kernel) {
  int w = origen.width;
  int h = origen.height;
  int kw = kernel.length;
  int offset = kw / 2;

  PImage resultado = createImage(w, h, RGB);
  origen.loadPixels();
  resultado.loadPixels();

  for (int py = 0; py < h; py++) {
    for (int px = 0; px < w; px++) {
      float sum = 0;

      for (int ky = 0; ky < kw; ky++) {
        for (int kx = 0; kx < kw; kx++) {
          int imgX = constrain(px + kx - offset, 0, w-1);
          int imgY = constrain(py + ky - offset, 0, h-1);
          sum += green(origen.pixels[imgY * w + imgX]) * kernel[ky][kx];
        }
      }

      resultado.pixels[py * w + px] = color(constrain(sum, 0, 255));
    }
  }

  resultado.updatePixels();
  return resultado;
}
```
De la forma anteriormente descrita se realizan la mayoría de operaciones, sin embargo, para Sobel Magnitud es necesario crear un método específico que calcule la magnitud de sobel X y sobel Y

```java
PImage aplicarSobel(PImage origen) {
  PImage resultado = createImage(origen.width, origen.height, RGB);
  PImage sobelX = convolver(origen, kernelSobelX);
  PImage sobelY = convolver(origen, kernelSobelY);

  sobelX.loadPixels();
  sobelY.loadPixels();
  resultado.loadPixels();

  for (int i = 0; i < origen.pixels.length; i++) {
    float gx = green(sobelX.pixels[i]);
    float gy = green(sobelY.pixels[i]);
    float magnitud = sqrt(gx*gx + gy*gy);

    if (magnitud < 50) magnitud = 0;
    else magnitud = min(255, magnitud);

    resultado.pixels[i] = color(magnitud);
  }

  resultado.updatePixels();
  return resultado;
}
```

Para todos los efectos artísticos se crearon métodos especiales que modifican los valores RGB de cada pixel según el filtro deseado, a continuación se presenta uno de estos, el método usado para generar el filtro negativo

```java
PImage efectoNegativo(PImage origen) {
  PImage resultado = origen.get();
  resultado.loadPixels();

  for (int i = 0; i < resultado.pixels.length; i++) {
    resultado.pixels[i] = color(
      255 - red(resultado.pixels[i]),
      255 - green(resultado.pixels[i]),
      255 - blue(resultado.pixels[i])
    );
  }

  resultado.updatePixels();
  return resultado;
}
```
Luego de crear todos los métodos para aplicar el procesamiento, simplemente se invocan y se pasan los parametros requeridos por cada método (imagen y kernel de ser necesario)

Ejemplo de invocación de métodos para la primera fila

```java
//Original
image(imgOriginal, x, y);
text("Original", x, y - 5);

// Sobel X
image(convolver(imgOriginal, kernelSobelX), x + spacing, y);
text("Sobel X", x + spacing, y - 5);

// Sobel Y
image(convolver(imgOriginal, kernelSobelY), x + spacing * 2, y);
text("Sobel Y", x + spacing * 2, y - 5);

// Sobel Magnitud
image(aplicarSobel(imgOriginal), x + spacing * 3, y);
text("Sobel Magnitud", x + spacing * 3, y - 5);
```

## Prompts utilizados:

Genera un Script en processing (.pde) que use kernels personalizados para aplicar multiples tipos de filtros a una imagen de prueba, para luego mostrar estos filtros junto a la imagen original en una ventana de processing

Genera métodos especiales para aplicar filtros sepia, negativo, y demás filtros artísticos a una imagen en processing

## Aprendizajes y dificultades:
Este taller permitió entender cómo funcionan los operadores de gradiente para detección de bordes, la diferencia entre detectar bordes (Sobel) y aplicar filtros de convolución genéricos, y cómo combinar detección de bordes con efectos artísticos para crear visualizaciones interesantes. La principal dificultad fue comprender cómo los kernels de convolución afectan cada píxel y cómo el umbral define qué constituye un "borde" versus ruido en la imagen.