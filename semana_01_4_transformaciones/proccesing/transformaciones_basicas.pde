final int CANVAS_W = 800;
final int CANVAS_H = 600;

float desplazamientoX = 0;
float factorEscala = 1;

float relojSegundos() {
  return millis() * 0.001;
}

float pulsoEscala() {
  return 1.0 + sin(millis() * 0.002) * 0.5;
}

void settings() {
  size(CANVAS_W, CANVAS_H, P3D);
}

void setup() {
  background(10, 18, 28);
}

void dibujarCuboPrincipal() {
  pushMatrix();

    float tiempo = relojSegundos();
    float vaivenX = sin(tiempo) * 150;
    float vaivenY = cos(tiempo) * 80;
    translate(vaivenX, vaivenY, 0);

    rotateX(frameCount * 0.01);
    rotateY(frameCount * 0.02);
    rotateZ(frameCount * 0.005);

    float escalaActual = pulsoEscala();
    scale(escalaActual);

    fill(40, 210, 190);
    stroke(180, 255, 246);
    strokeWeight(1);
    box(120);

    desplazamientoX = vaivenX;
    factorEscala = escalaActual;

  popMatrix();
}

void dibujarCuboSatelite() {
  pushMatrix();

    float orbitaSeg = millis() * 0.002;
    float posicionOrbitalX = sin(orbitaSeg) * 220;
    float posicionOrbitalY = cos(orbitaSeg) * 220;
    translate(posicionOrbitalX, posicionOrbitalY, 0);

    rotateY(frameCount * 0.05);
    rotateX(frameCount * 0.03);

    scale(0.4);

    fill(255, 80, 120);
    stroke(255, 180, 200);
    box(120);

  popMatrix();
}

void dibujarHUD() {
  pushMatrix();
    translate(-width/2 + 20, -height/2 + 30, 0);
    fill(235, 252, 255);
    textSize(14);
    text("Tiempo (ms): " + millis(), 0, 0);
    text("Frame: " + frameCount, 0, 20);
    text("Onda X: " + nf(desplazamientoX, 1, 1), 0, 40);
    text("Escala: " + nf(factorEscala, 1, 2), 0, 60);
  popMatrix();
}

void draw() {
  background(10, 18, 28);

  lights();

  translate(width/2, height/2, 0);

  dibujarCuboPrincipal();
  dibujarCuboSatelite();
  dibujarHUD();
}
