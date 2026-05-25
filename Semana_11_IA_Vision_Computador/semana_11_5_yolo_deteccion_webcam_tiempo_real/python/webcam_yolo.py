from ultralytics import YOLO
import cv2,time


frame_skip = 1 #Cantidad de frames que se saltan
count = 0

tiempo_previo = 0 # Variable para almacenar el tiempo del frame anterior
fps = 0 # Variable para almacenar los FPS


# Menu de opciones para mostrar todas las detecciones o una clase específica
print("\nMenu de deteccion con YoloV8 y Webcam")
print("1 - Mostrar todas las detecciones")
print("2 - Mostrar una clase específica")
opcion = int(input("\nSeleccione una opción: "))

if opcion == 2:
    clase_especifica = input("Ingrese la clase específica a mostrar (ID - ver COCO_clases.txt ): ")




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

    tiempo_actual = time.time() # Obtener el tiempo actual para calcular los FPS
    
    
    if opcion == 2:
        # Realizar la detección de objetos utilizando el modelo YOLOv8 y mostrar solo la clase específica
        results = model.predict(frame,imgsz=640,classes=[int(clase_especifica)])
    else:
        # Realizar la detección de objetos utilizando el modelo YOLOv8
        results = model.predict(frame,imgsz=640)

    # Dibujar los bounding boxes y etiquetas en la imagen utilizando plot
    test_image = results[0].plot(line_width=2)

    # Calcular el tiempo transcurrido desde el último frame para calcular los FPS
    dif_tiempo = tiempo_actual - tiempo_previo
    tiempo_previo = tiempo_actual

    # Calcular los FPS solo si el tiempo transcurrido es mayor a cero para evitar divisiones por cero
    if dif_tiempo > 0:
        fps = 1 / dif_tiempo

    # Posicionar el texto de los FPS en la imagen
    texto_fps = f"FPS: {int(fps)}"
    cv2.putText(test_image, texto_fps, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                1.0, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Mostrar la imagen con las detecciones y los FPS
    cv2.imshow('Detecciones YOLOv8',test_image)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()