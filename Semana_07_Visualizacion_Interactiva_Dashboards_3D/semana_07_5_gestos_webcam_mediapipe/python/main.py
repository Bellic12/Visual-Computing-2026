import math
import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def distance(p1, p2):
    return math.sqrt(
        (p1.x - p2.x)**2 +
        (p1.y - p2.y)**2
    )

def count_fingers(hand_landmarks):
    fingers = []

    # Índice, medio, anular, meñique
    tips = [8, 12, 16, 20]
    bases = [6, 10, 14, 18]

    for tip, base in zip(tips, bases):
        if hand_landmarks[tip].y < hand_landmarks[base].y:
            fingers.append(1)
        else:
            fingers.append(0)

    # Pulgar (caso especial → eje X)
    if hand_landmarks[4].x > hand_landmarks[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    return sum(fingers)

# Configuración del modelo
base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2
)

detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: no se pudo abrir la cámara")
    exit()

color = (0, 0, 0)  # negro por defecto
cube_pos = [300, 300]
cube_size = 80
cube_active = False
dragging = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # MediaPipe espera imagen tipo mp.Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    result = detector.detect(mp_image)
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    no_hand_detected = not result.hand_landmarks   

    # Dibujar puntos manualmente (simplificado)
    if result.hand_landmarks:
        for hand in result.hand_landmarks:
            points = []

            for landmark in hand:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 5, (128, 0, 0), -1)
                points.append([x, y])

            points = np.array(points)
            hull = cv2.convexHull(points)
            cv2.fillConvexPoly(mask, hull, 255)
            mask = cv2.GaussianBlur(mask, (21, 21), 0)

            mask_float = mask.astype(np.float32) / 255.0
            mask_float = np.expand_dims(mask_float, axis=2)  # para RGB

            mask_inv = cv2.bitwise_not(mask)
            background = np.full(frame.shape, color, dtype=np.uint8)

            # hacer el fondo más "suave"
            background = cv2.addWeighted(background, 0.7, frame, 0.3, 0)

            frame = (frame * mask_float + background * (1 - mask_float)).astype(np.uint8)

            count = count_fingers(hand)
            cv2.putText(frame, f"Fingers: {count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)

            if count == 1:
                color=(0,0,0)
            elif count == 2: 
                color=(128,128,128)
            elif count == 3:
                color=(255,255,255)

            thumb = hand[4]
            index = hand[8]

            dist = distance(thumb, index)
            cv2.putText(frame, f"Dist: {dist:.2f}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

            # Posición del dedo índice
            index_x = int(index.x * frame.shape[1])
            index_y = int(index.y * frame.shape[0])

            # Detectar pinch
            pinch = dist < 0.08

            # Crear cubo con mano abierta
            if count == 5:
                cube_active = True

            # Interacción con el cubo
            if cube_active:
                # Verificar si el dedo está dentro del cubo
                inside_cube = (
                    cube_pos[0] < index_x < cube_pos[0] + cube_size and
                    cube_pos[1] < index_y < cube_pos[1] + cube_size
                )

                # Empezar a arrastrar
                if inside_cube and pinch:
                    dragging = True

                # Mover cubo
                if dragging:
                    cube_pos[0] = int(0.7 * cube_pos[0] + 0.3 * (index_x - cube_size // 2))
                    cube_pos[1] = int(0.7 * cube_pos[1] + 0.3 * (index_y - cube_size // 2))

                # Soltar cubo
                if not pinch:
                    dragging = False

    else:
        bg = np.full(frame.shape, color, dtype=np.uint8)
        frame = cv2.addWeighted(frame, 0.2, bg, 0.8, 0)

    # Dibujar cubo
    if cube_active:
        cv2.rectangle(
            frame,
            (cube_pos[0], cube_pos[1]),
            (cube_pos[0] + cube_size, cube_pos[1] + cube_size),
            (255, 0, 255),
            -1
        )

        inside_cube = (
            cube_pos[0] < index_x < cube_pos[0] + cube_size and
            cube_pos[1] < index_y < cube_pos[1] + cube_size
        )

        # 🧲 DRAG
        if inside_cube and pinch:
            dragging = True

        if dragging:
            cube_pos[0] = int(0.7 * cube_pos[0] + 0.3 * (index_x - cube_size // 2))
            cube_pos[1] = int(0.7 * cube_pos[1] + 0.3 * (index_y - cube_size // 2))

        if not pinch:
            dragging = False

        # 💥 DELETE
        if count == 0 and inside_cube:
            cube_active = False
            dragging = False

    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()