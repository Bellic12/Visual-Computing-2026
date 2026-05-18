
PImage imgOriginal;

// Kernels
float[][] kernelSobelX = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
float[][] kernelSobelY = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
float[][] kernelEdge = {{-1, -1, -1}, {-1, 8, -1}, {-1, -1, -1}};
float[][] kernelSharpen = {{0, -1, 0}, {-1, 5, -1}, {0, -1, 0}};
float[][] kernelBlur = {{1/9.0, 1/9.0, 1/9.0}, {1/9.0, 1/9.0, 1/9.0}, {1/9.0, 1/9.0, 1/9.0}};
float[][] kernelGauss = {{1/16.0, 2/16.0, 1/16.0}, {2/16.0, 4/16.0, 2/16.0}, {1/16.0, 2/16.0, 1/16.0}};
float[][] kernelEmboss = {{-2, -1, 0}, {-1, 1, 1}, {0, 1, 2}};

void setup() {
  size(900, 800);
  pixelDensity(1);

  // CARGAR IMAGEN DESDE ARCHIVO
  imgOriginal = loadImage("../../media/bike.jpg");
  imgOriginal.resize(180, 130);
}

void draw() {
  background(30);
  fill(255);
  textSize(12);

  int x = 10;
  int y = 30;
  int spacing = 200;

  // ==================== FILA 1: FILTROS BÁSICOS ====================
  // Original
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

  // ==================== FILA 2: FILTROS DE PROCESAMIENTO ====================
  // Edge Detection
  image(convolver(imgOriginal, kernelEdge), x, y + 160);
  text("Edge Detection", x, y + 155);

  // Sharpen
  image(convolver(imgOriginal, kernelSharpen), x + spacing, y + 160);
  text("Sharpen", x + spacing, y + 155);

  // Box Blur
  image(convolver(imgOriginal, kernelBlur), x + spacing * 2, y + 160);
  text("Box Blur", x + spacing * 2, y + 155);

  // Gaussian Blur
  image(convolver(imgOriginal, kernelGauss), x + spacing * 3, y + 160);
  text("Gaussian Blur", x + spacing * 3, y + 155);

  // ==================== FILA 3: EFECTOS ARTÍSTICOS ====================
  // Negativo
  image(efectoNegativo(imgOriginal), x, y + 320);
  text("Negativo", x, y + 315);

  // Sepia
  image(efectoSepia(imgOriginal), x + spacing, y + 320);
  text("Sepia", x + spacing, y + 315);

  // Posterizar
  image(efectoPosterizar(imgOriginal), x + spacing * 2, y + 320);
  text("Posterizar", x + spacing * 2, y + 315);

  // Relieve (Emboss)
  image(convolver(imgOriginal, kernelEmboss), x + spacing * 3, y + 320);
  text("Relieve", x + spacing * 3, y + 315);

  // ==================== FILA 4: BORDES ARTÍSTICOS ====================
  // Borde artístico con inversión de color
  image(bordeArtisticoInvertido(imgOriginal), x, y + 480);
  text("Borde Invertido", x, y + 475);

  // Borde con color falso
  image(bordeColorFalso(imgOriginal), x + spacing, y + 480);
  text("Borde Color Falso", x + spacing, y + 475);

  // Borde estilo solarizado
  image(bordeSolarizado(imgOriginal), x + spacing * 2, y + 480);
  text("Borde Solarizado", x + spacing * 2, y + 475);

  // Contorno estilo dibujo
  image(estiloDibujo(imgOriginal), x + spacing * 3, y + 480);
  text("Estilo Dibujo", x + spacing * 3, y + 475);
}

// =============================================================================
// FILTRO SOBEL (magnitud)
// =============================================================================

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

// =============================================================================
// CONVOLUCIÓN
// =============================================================================

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

// =============================================================================
// EFECTOS ARTÍSTICOS
// =============================================================================

// Negativo
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

// Sepia
PImage efectoSepia(PImage origen) {
  PImage resultado = origen.get();
  resultado.loadPixels();

  for (int i = 0; i < resultado.pixels.length; i++) {
    float r = red(resultado.pixels[i]);
    float g = green(resultado.pixels[i]);
    float b = blue(resultado.pixels[i]);

    float nuevoR = r * 0.393 + g * 0.769 + b * 0.189;
    float nuevoG = r * 0.349 + g * 0.686 + b * 0.168;
    float nuevoB = r * 0.272 + g * 0.534 + b * 0.131;

    resultado.pixels[i] = color(constrain(nuevoR, 0, 255), constrain(nuevoG, 0, 255), constrain(nuevoB, 0, 255));
  }

  resultado.updatePixels();
  return resultado;
}

// Posterizar (reducir colores)
PImage efectoPosterizar(PImage origen) {
  PImage resultado = origen.get();
  resultado.loadPixels();
  int niveles = 4;

  for (int i = 0; i < resultado.pixels.length; i++) {
    float r = red(resultado.pixels[i]);
    float g = green(resultado.pixels[i]);
    float b = blue(resultado.pixels[i]);

    r = floor(r / 255 * niveles) * (255 / niveles);
    g = floor(g / 255 * niveles) * (255 / niveles);
    b = floor(b / 255 * niveles) * (255 / niveles);

    resultado.pixels[i] = color(r, g, b);
  }

  resultado.updatePixels();
  return resultado;
}

// Borde artístico con inversión de color
PImage bordeArtisticoInvertido(PImage origen) {
  PImage resultado = createImage(origen.width, origen.height, RGB);
  PImage bordes = aplicarSobel(origen);

  origen.loadPixels();
  bordes.loadPixels();
  resultado.loadPixels();

  for (int i = 0; i < origen.pixels.length; i++) {
    float magnitud = green(bordes.pixels[i]);

    if (magnitud > 50) {
      // Borde: negativo del color original
      resultado.pixels[i] = color(
        255 - red(origen.pixels[i]),
        255 - green(origen.pixels[i]),
        255 - blue(origen.pixels[i])
      );
    } else {
      // Sin borde: gris oscuro
      float gris = (red(origen.pixels[i]) + green(origen.pixels[i]) + blue(origen.pixels[i])) / 3;
      resultado.pixels[i] = color(gris * 0.3);
    }
  }

  resultado.updatePixels();
  return resultado;
}

// Borde con color falso (basado en dirección del gradiente)
PImage bordeColorFalso(PImage origen) {
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

    if (magnitud < 50) {
      resultado.pixels[i] = color(0);
    } else {
      // Color basado en dirección del gradiente
      float angulo = atan2(gy, gx);
      float r = 128 + 127 * sin(angulo);
      float g = 128 + 127 * cos(angulo * 2);
      float b = magnitud;
      resultado.pixels[i] = color(constrain(r, 0, 255), constrain(g, 0, 255), constrain(b, 0, 255));
    }
  }

  resultado.updatePixels();
  return resultado;
}

// Borde solarizado (estilo Instagram)
PImage bordeSolarizado(PImage origen) {
  PImage resultado = createImage(origen.width, origen.height, RGB);
  PImage bordes = aplicarSobel(origen);

  origen.loadPixels();
  bordes.loadPixels();
  resultado.loadPixels();

  for (int i = 0; i < origen.pixels.length; i++) {
    float magnitud = green(bordes.pixels[i]);

    if (magnitud > 50) {
      // Borde: color saturado
      float r = red(origen.pixels[i]);
      float g = green(origen.pixels[i]);
      float b = blue(origen.pixels[i]);

      // Aumentar saturación
      float maximo = max(r, max(g, b));
      float minimo = min(r, min(g, b));
      float prom = (r + g + b) / 3;

      r = prom + (r - prom) * 1.5;
      g = prom + (g - prom) * 1.5;
      b = prom + (b - prom) * 1.5;

      resultado.pixels[i] = color(constrain(r, 0, 255), constrain(g, 0, 255), constrain(b, 0, 255));
    } else {
      // Sin borde: casi negro
      resultado.pixels[i] = color(20, 20, 20);
    }
  }

  resultado.updatePixels();
  return resultado;
}

// Estilo dibujo (lápiz)
PImage estiloDibujo(PImage origen) {
  PImage resultado = createImage(origen.width, origen.height, RGB);
  PImage bordes = aplicarSobel(origen);

  origen.loadPixels();
  bordes.loadPixels();
  resultado.loadPixels();

  for (int i = 0; i < origen.pixels.length; i++) {
    float magnitud = green(bordes.pixels[i]);

    if (magnitud > 50) {
      // Borde: blanco
      resultado.pixels[i] = color(255);
    } else {
      // Sin borde: escala de grises basada en original
      float gris = (red(origen.pixels[i]) + green(origen.pixels[i]) + blue(origen.pixels[i])) / 3;
      resultado.pixels[i] = color(gris);
    }
  }

  resultado.updatePixels();
  return resultado;
}
