"""Pintura interactiva controlada por gestos y comandos de voz.

Uso:
    python pintura_interactiva.py

Controles:
- Mano (MediaPipe):
    pinza (indice + pulgar) para dibujar
    mano abierta para pausar y cambiar tipo de pincel
- Voz (speech_recognition):
    rojo, verde, azul, amarillo, negro, blanco
    limpiar, guardar, pincel, borrar
- Teclado:
    q: salir
    c: limpiar lienzo
    s: guardar imagen
"""

from __future__ import annotations

import os
import queue
import threading
import time
from datetime import datetime
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

try:
    import speech_recognition as sr
except Exception:
    sr = None


# Colores en formato BGR para OpenCV.
COLOR_MAP = {
    "rojo": (0, 0, 255),
    "verde": (0, 255, 0),
    "azul": (255, 0, 0),
    "amarillo": (0, 255, 255),
    "negro": (0, 0, 0),
    "blanco": (255, 255, 255),
}

BRUSH_TYPES = ["redondo", "cuadrado", "spray"]


class VoiceListener(threading.Thread):
    """Escucha en segundo plano y envia comandos reconocidos a una cola."""

    def __init__(self, command_queue: queue.Queue[str]):
        super().__init__(daemon=True)
        self.command_queue = command_queue
        self.stop_event = threading.Event()
        self.enabled = sr is not None

    def run(self) -> None:
        if not self.enabled:
            return

        recognizer = sr.Recognizer()

        try:
            mic = sr.Microphone()
        except Exception:
            self.enabled = False
            return

        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)

        while not self.stop_event.is_set():
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=2.5)
            except sr.WaitTimeoutError:
                continue
            except Exception:
                continue

            try:
                text = recognizer.recognize_google(audio, language="es-ES")
            except Exception:
                continue

            command = text.strip().lower()
            if command:
                self.command_queue.put(command)

    def stop(self) -> None:
        self.stop_event.set()


def _distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    return float(np.hypot(p1[0] - p2[0], p1[1] - p2[1]))


def detect_hand_gesture(
    frame_bgr: np.ndarray,
    hands,
) -> tuple[tuple[int, int] | None, bool, bool, int]:
    """Retorna posicion del indice, estado de gesto y cantidad de dedos extendidos."""
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if not results.multi_hand_landmarks:
        return None, False, False, 0

    hand_landmarks = results.multi_hand_landmarks[0]
    h, w, _ = frame_bgr.shape
    lm = hand_landmarks.landmark

    index_tip = (int(lm[8].x * w), int(lm[8].y * h))
    thumb_tip = (lm[4].x * w, lm[4].y * h)
    index_tip_float = (lm[8].x * w, lm[8].y * h)
    palm_left = (lm[5].x * w, lm[5].y * h)
    palm_right = (lm[17].x * w, lm[17].y * h)
    palm_size = max(_distance(palm_left, palm_right), 1.0)

    pinch_distance = _distance(thumb_tip, index_tip_float)
    is_pinch = pinch_distance < 0.45 * palm_size

    # Mano abierta: dedos indice, medio, anular y menique extendidos.
    fingers_extended = (
        lm[8].y < lm[6].y
        and lm[12].y < lm[10].y
        and lm[16].y < lm[14].y
        and lm[20].y < lm[18].y
    )
    is_open_hand = fingers_extended and not is_pinch

    finger_count = sum(
        [
            lm[8].y < lm[6].y,
            lm[12].y < lm[10].y,
            lm[16].y < lm[14].y,
            lm[20].y < lm[18].y,
        ]
    )

    return index_tip, is_pinch, is_open_hand, finger_count


def draw_stroke(
    canvas: np.ndarray,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    thickness: int,
    brush_type: str,
) -> None:
    """Dibuja un trazo entre dos puntos segun el tipo de pincel."""
    if brush_type == "cuadrado":
        steps = int(max(abs(end[0] - start[0]), abs(end[1] - start[1])) / 3) + 1
        half = max(thickness // 2, 1)
        for i in range(steps + 1):
            t = i / max(steps, 1)
            x = int(start[0] + (end[0] - start[0]) * t)
            y = int(start[1] + (end[1] - start[1]) * t)
            cv2.rectangle(canvas, (x - half, y - half), (x + half, y + half), color, -1)
        return

    if brush_type == "spray":
        radius = max(thickness, 6)
        points_per_step = 14
        steps = int(max(abs(end[0] - start[0]), abs(end[1] - start[1])) / 4) + 1
        for i in range(steps + 1):
            t = i / max(steps, 1)
            cx = int(start[0] + (end[0] - start[0]) * t)
            cy = int(start[1] + (end[1] - start[1]) * t)
            for _ in range(points_per_step):
                angle = np.random.uniform(0, 2 * np.pi)
                dist = np.random.uniform(0, radius)
                x = int(cx + np.cos(angle) * dist)
                y = int(cy + np.sin(angle) * dist)
                if 0 <= x < canvas.shape[1] and 0 <= y < canvas.shape[0]:
                    cv2.circle(canvas, (x, y), 1, color, -1)
        return

    cv2.line(canvas, start, end, color, thickness)


def ensure_media_dir() -> Path:
    """Garantiza que exista la carpeta media al nivel del taller."""
    script_dir = Path(__file__).resolve().parent
    media_dir = script_dir.parent / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    return media_dir


def save_canvas(canvas: np.ndarray) -> str:
    media_dir = ensure_media_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = media_dir / f"obra_{timestamp}.png"
    cv2.imwrite(str(out_path), canvas)
    return str(out_path)


def apply_voice_command(
    command: str,
    current_color: tuple[int, int, int],
    brush_thickness: int,
    eraser_mode: bool,
    canvas: np.ndarray,
) -> tuple[tuple[int, int, int], int, bool, str]:
    """Interpreta texto de voz y aplica cambios de estado de dibujo."""
    feedback = ""

    # Se busca por palabras clave para tolerar frases como "pon color rojo".
    for color_name, color_bgr in COLOR_MAP.items():
        if color_name in command:
            current_color = color_bgr
            eraser_mode = False
            feedback = f"Color: {color_name}"
            return current_color, brush_thickness, eraser_mode, feedback

    if "pincel" in command:
        eraser_mode = False
        brush_thickness = 5
        feedback = "Modo pincel"
    elif "borrar" in command or "goma" in command:
        eraser_mode = True
        brush_thickness = 30
        feedback = "Modo borrador"
    elif "limpiar" in command:
        canvas[:] = 255
        feedback = "Lienzo limpiado"
    elif "guardar" in command:
        output = save_canvas(canvas)
        feedback = f"Guardado: {os.path.basename(output)}"

    return current_color, brush_thickness, eraser_mode, feedback


def main() -> None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir la camara.")

    ok, frame = cap.read()
    if not ok:
        cap.release()
        raise RuntimeError("No se pudo capturar el primer frame.")

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    canvas = np.full((h, w, 3), 255, dtype=np.uint8)

    command_queue: queue.Queue[str] = queue.Queue()
    voice_listener = VoiceListener(command_queue)
    voice_listener.start()

    current_color = COLOR_MAP["rojo"]
    brush_thickness = 5
    eraser_mode = False
    last_point: tuple[int, int] | None = None
    gesture_status = "Pausa"
    brush_type_index = 0
    brush_type = BRUSH_TYPES[brush_type_index]
    last_brush_change = 0.0
    feedback_text = "Listo"
    feedback_until = 0.0

    mp_hands = mp.solutions.hands
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as hands:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            point, is_pinch, is_open_hand, finger_count = detect_hand_gesture(frame, hands)

            if point is not None:
                if is_pinch:
                    if last_point is None:
                        last_point = point

                    draw_color = (255, 255, 255) if eraser_mode else current_color
                    draw_stroke(canvas, last_point, point, draw_color, brush_thickness, brush_type)
                    last_point = point
                    gesture_status = f"Dibujando (pinza, {brush_type})"
                else:
                    last_point = None
                    if is_open_hand:
                        now = time.time()
                        if now - last_brush_change > 0.9:
                            brush_type_index = (brush_type_index + 1) % len(BRUSH_TYPES)
                            brush_type = BRUSH_TYPES[brush_type_index]
                            last_brush_change = now
                            feedback_text = f"Pincel: {brush_type}"
                            feedback_until = now + 2.0
                        gesture_status = f"Pausa (mano abierta: {finger_count} dedos)"
                    else:
                        gesture_status = f"Seguimiento ({finger_count} dedos)"

                cv2.circle(frame, point, 8, (0, 0, 0), 2)
            else:
                last_point = None
                gesture_status = "Sin mano"

            while not command_queue.empty():
                cmd = command_queue.get()
                current_color, brush_thickness, eraser_mode, new_feedback = apply_voice_command(
                    command=cmd,
                    current_color=current_color,
                    brush_thickness=brush_thickness,
                    eraser_mode=eraser_mode,
                    canvas=canvas,
                )
                if new_feedback:
                    feedback_text = new_feedback
                    feedback_until = time.time() + 2.5

            # Mezcla del lienzo con la imagen de camara para visualizacion en vivo.
            blended = cv2.addWeighted(frame, 0.55, canvas, 0.45, 0)

            mode_text = "Borrador" if eraser_mode else "Pincel"
            color_text = f"Color BGR: {current_color}"
            cv2.putText(
                blended,
                f"Modo: {mode_text}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (20, 20, 20),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                blended,
                color_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (20, 20, 20),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                blended,
                f"Tipo: {brush_type}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (20, 20, 20),
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                blended,
                f"Gesto: {gesture_status}",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (20, 20, 20),
                2,
                cv2.LINE_AA,
            )

            if time.time() < feedback_until:
                cv2.putText(
                    blended,
                    feedback_text,
                    (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (30, 30, 30),
                    2,
                    cv2.LINE_AA,
                )

            cv2.imshow("Pintura interactiva (voz + gestos)", blended)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("c"):
                canvas[:] = 255
                feedback_text = "Lienzo limpiado"
                feedback_until = time.time() + 2.5
            if key == ord("s"):
                output = save_canvas(canvas)
                feedback_text = f"Guardado: {os.path.basename(output)}"
                feedback_until = time.time() + 2.5

    voice_listener.stop()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
