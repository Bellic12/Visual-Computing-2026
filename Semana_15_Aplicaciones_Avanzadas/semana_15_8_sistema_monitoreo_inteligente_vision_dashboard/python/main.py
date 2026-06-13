from ultralytics import YOLO
import cv2,time


frame_skip = 1 #Cantidad de frames que se saltan
count = 0

# Cargar el modelo YOLOv8 preentrenado
model = YOLO('yolov8n.pt')
# Iniciar la captura de la webcam
cap = cv2.VideoCapture(0)

# verificar si la cámara se abrió correctamente
if not cap.isOpened():
    print("No se pudo abrir la cámara o el video.")
    raise SystemExit

while True: # repertir hasta que se presione 'q' para salir
    ret, frame = cap.read()
    if not ret:
        print("No hay más frames.")
        break

    count += 1
    if count % frame_skip != 0:
        continue
    
    # Realizar la detección de objetos utilizando el modelo YOLOv8
    results = model.predict(frame,imgsz=640)
    # Dibujar los bounding boxes y etiquetas en la imagen utilizando plot
    test_image = results[0].plot(line_width=2)
    
    # Mostrar la imagen con las detecciones y los FPS
    cv2.imshow('Detecciones YOLOv8',test_image)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()