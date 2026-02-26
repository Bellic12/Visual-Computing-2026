float x,y;
float xpos,ypos,zpos;
float xrot,yrot;

void setup() {
  size(800,800,P3D);
  x = width/2;
  y = height/2;
  
  xpos = x;
  ypos = y;
  zpos = 50;
  
  xrot = 0;
  yrot = 0;
  
  float fov = PI/3.0;
  float cameraZ = (height/2.0) / tan(fov/2.0);
  perspective(fov, float(width)/float(height),cameraZ/10.0, cameraZ*10.0);
}

void draw() {
  
  //
  background(0);
  
  ortho();
  pushMatrix();
  
  translate(xpos,ypos,zpos);
  rotateX(radians(xrot));
  rotateY(radians(yrot));

  
  pushMatrix();
  translate(0,0,100);
  rotateX(PI/8);
  box(100);
  popMatrix();
  
  pushMatrix();
  translate(0,0,200);
  sphere(50);
  popMatrix();
  
  pushMatrix();
  translate(0,0,0);
  sphere(50);
  popMatrix();
  
  popMatrix();
  
  
  // Controles de cámara
  if (keyPressed) {
    // Controles de traslación
    if (keyCode == RIGHT) xpos -= 2;
    if (keyCode == LEFT)  xpos += 2;
    if (keyCode == UP)  ypos += 2;
    if (keyCode == DOWN)  ypos -= 2;
    if (key == 'z') zpos -=2;
    if (key == 'x') zpos +=2;
    
    //Coontroles de rotación
    if (key == 'a') yrot +=2;
    if (key == 'd') yrot -=2;
    if (key == 'w') xrot -=2;
    if (key == 's') xrot +=2;
  }
  
  
  
  
  
  
  


}
