"""
main_multimodal.py
Sistema de interfaces multimodales: voz + gestos en tiempo real.
Refactorizado para usar la API moderna de MediaPipe Tasks.
"""

import cv2
import mediapipe as mp
try:
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
except ImportError:
    pass  # Si falla, el error se atrapará más adelante

import urllib.request
import os
import numpy as np
import threading
import time
import speech_recognition as sr
import sounddevice as sd
import pygame
import sys

# ── Configuración ────────────────────────────────────────────────────
ANCHO_VENTANA  = 1100
ALTO_VENTANA   = 600
ANCHO_CAM      = 520
CAMARA_ID      = 0
IDIOMA_VOZ     = "es-ES"
FPS_OBJETIVO   = 30

# Descargar modelo de MediaPipe si no existe
MODEL_PATH = 'hand_landmarker.task'
if not os.path.exists(MODEL_PATH):
    print("📥 Descargando modelo de manos de MediaPipe (esto solo pasa una vez)...")
    try:
        urllib.request.urlretrieve(
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", 
            MODEL_PATH
        )
        print("✅ Modelo descargado.")
    except Exception as e:
        print(f"Error descargando el modelo: {e}")

# ── Estado global compartido entre hilos ─────────────────────────────
estado_global = {
    "gesto_actual":   "ninguno",
    "comando_actual": None,
    "accion":         "Esperando entrada...",
    "color":          (0, 100, 220),
    "posicion":       [ANCHO_VENTANA // 2, ALTO_VENTANA // 2],
    "angulo":         0,
    "animando":       False,
    "info_visible":   False,
    "frame_cam":      None,
    "ejecutando":     True,
}
lock = threading.Lock()


# ── Módulo de gestos (hilo de cámara) ────────────────────────────────
def hilo_camara():
    """Captura frames de la cámara y detecta gestos usando la API Tasks."""
    
    # Configurar la nueva API de MediaPipe
    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
    detector = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(CAMARA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Conexiones para dibujar el esqueleto manualmente
    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (17, 18), (18, 19), (19, 20),
        (0, 17)
    ]

    while estado_global["ejecutando"]:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)  # espejo horizontal
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Procesar con la nueva API
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        detection_result = detector.detect(mp_image)
        
        frame_ann = frame.copy()
        gesto = "ninguno"

        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                # 1. Dibujar landmarks manualmente (reemplaza a mp.solutions.drawing_utils)
                h, w, _ = frame_ann.shape
                puntos = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
                
                for c in HAND_CONNECTIONS:
                    cv2.line(frame_ann, puntos[c[0]], puntos[c[1]], (0, 255, 0), 2)
                for p in puntos:
                    cv2.circle(frame_ann, p, 4, (0, 0, 255), -1)

                # 2. Clasificar el gesto
                # Pulgar
                dedos = [hand_landmarks[4].x < hand_landmarks[3].x]
                # Índice, medio, anular, meñique
                for p in [8, 12, 16, 20]:
                    dedos.append(hand_landmarks[p].y < hand_landmarks[p-2].y)

                total = sum(dedos)
                if total == 5:
                    gesto = "mano_abierta"
                elif total == 0:
                    gesto = "puno"
                elif total == 1 and dedos[1]:
                    gesto = "un_dedo"
                elif total == 2 and dedos[1] and dedos[2]:
                    gesto = "dos_dedos"
                elif total == 3 and dedos[1] and dedos[2] and dedos[3]:
                    gesto = "tres_dedos"
                else:
                    gesto = "desconocido"

        with lock:
            if gesto != "ninguno":
                estado_global["gesto_actual"] = gesto
                estado_global["tiempo_gesto"] = time.time()
            else:
                # Mantener el gesto vivo por 2 segundos para dar tiempo a que la voz lo alcance
                if time.time() - estado_global.get("tiempo_gesto", 0) > 2.0:
                    estado_global["gesto_actual"] = "ninguno"
                    
            estado_global["frame_cam"] = frame_ann

    cap.release()


# ── Módulo de voz (hilo de audio) ────────────────────────────────────
COMANDOS_VOZ = {
    "cambiar": ["cambiar", "color"],
    "mover":   ["mover", "mueve"],
    "rotar":   ["rotar", "girar", "gira"],
    "mostrar": ["mostrar", "muestra"],
    "azul":    ["azul"],
    "rojo":    ["rojo"],
    "verde":   ["verde"],
    "reset":   ["reset", "reiniciar"],
    "parar":   ["parar", "stop"],
}

def normalizar_voz(texto):
    texto = texto.lower()
    for cmd, variantes in COMANDOS_VOZ.items():
        for v in variantes:
            if v in texto:
                return cmd
    return None

def hilo_voz():
    """Escucha el micrófono usando sounddevice."""
    reconocedor = sr.Recognizer()
    fs = 16000
    duracion = 2.5
    
    while estado_global["ejecutando"]:
        try:
            grabacion = sd.rec(int(duracion * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()
            
            # Calcular volumen para depurar si el micrófono sirve
            volumen = np.abs(grabacion).mean()
            if volumen < 50:
                print(f"🔇 Micrófono muy bajo o silenciado (Volumen: {volumen:.1f})")
                
            audio = sr.AudioData(grabacion.tobytes(), fs, 2)
            
            texto = reconocedor.recognize_google(audio, language=IDIOMA_VOZ)
            cmd   = normalizar_voz(texto)
            if texto.strip():
                print(f"🗣️ Escuché: '{texto}' -> Comando: {cmd}")
            with lock:
                estado_global["comando_actual"] = cmd
        except sr.UnknownValueError:
            pass # No reconoció palabras
        except sr.RequestError:
            print("🌐 Error de internet al contactar a Google.")
            time.sleep(2)


# ── Motor multimodal ─────────────────────────────────────────────────
COLORES = {
    "azul":  (0, 100, 220), "rojo": (220, 40, 40), "verde": (40, 180, 80),
}
LISTA_COLORES = list(COLORES.values()) + [(255,200,0),(160,40,220),(255,140,0)]
_idx_color = 0

def evaluar_accion():
    global _idx_color
    with lock:
        g = estado_global["gesto_actual"]
        c = estado_global["comando_actual"]
        estado_global["comando_actual"] = None

    if c is None:
        return

    if g == "mano_abierta":
        if c == "cambiar":
            _idx_color = (_idx_color + 1) % len(LISTA_COLORES)
            with lock: estado_global["color"] = LISTA_COLORES[_idx_color]
        elif c in COLORES:
            with lock: estado_global["color"] = COLORES[c]
    elif g == "dos_dedos":
        if c == "mover":
            dx, dy = np.random.randint(-100, 100), np.random.randint(-80, 80)
            with lock:
                estado_global["posicion"][0] = int(np.clip(estado_global["posicion"][0]+dx, 100, ANCHO_VENTANA-100))
                estado_global["posicion"][1] = int(np.clip(estado_global["posicion"][1]+dy, 100, ALTO_VENTANA-100))
        elif c == "rotar":
            with lock: estado_global["angulo"] = (estado_global["angulo"] + 45) % 360
    elif g == "puno" and c == "parar":
        with lock: estado_global["animando"] = False
    elif g == "tres_dedos" and c == "reset":
        with lock:
            estado_global["color"]    = (0, 100, 220)
            estado_global["posicion"] = [ANCHO_VENTANA//2, ALTO_VENTANA//2]
            estado_global["angulo"]   = 0

    with lock: estado_global["accion"] = f"{g} + {c}"


# ── Renderizado con Pygame ────────────────────────────────────────────
def dibujar_pygame(pantalla, font_sm, font_md):
    with lock:
        s = dict(estado_global)

    pantalla.fill((18, 18, 28))

    if s["frame_cam"] is not None:
        frame_rgb = cv2.cvtColor(s["frame_cam"], cv2.COLOR_BGR2RGB)
        frame_res = cv2.resize(frame_rgb, (ANCHO_CAM, 390))
        surf = pygame.surfarray.make_surface(frame_res.swapaxes(0, 1))
        pantalla.blit(surf, (10, 10))

    cx, cy = s["posicion"]
    r, ang  = 60, s["angulo"]
    puntos  = [
        (cx + r * np.cos(np.radians(ang + i*60)),
         cy + r * np.sin(np.radians(ang + i*60)))
        for i in range(6)
    ]
    pygame.draw.polygon(pantalla, s["color"], puntos)
    pygame.draw.polygon(pantalla, tuple(min(255,c+80) for c in s["color"]), puntos, 2)
    
    # Dibujar un indicador para que la rotación sea súper evidente
    punto_frente = (int(cx + r * np.cos(np.radians(ang))), int(cy + r * np.sin(np.radians(ang))))
    pygame.draw.line(pantalla, (255, 255, 255), (cx, cy), punto_frente, 3)
    pygame.draw.circle(pantalla, (255, 255, 255), punto_frente, 6)

    hud_items = [
        (f"Gesto:   {s['gesto_actual']}",  (100, 220, 255)),
        (f"Accion:  {s['accion']}",        (255, 220, 100)),
        (f"Angulo:  {s['angulo']}°",       (160, 160, 200)),
        (f"Pos:     {s['posicion']}",      (160, 160, 200)),
        ("[Q] Salir",                      (100, 100, 140)),
    ]
    for i, (texto, color) in enumerate(hud_items):
        surf_t = font_sm.render(texto, True, color)
        pantalla.blit(surf_t, (ANCHO_CAM + 20, 20 + i * 30))

    pygame.display.flip()


# ── Main ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption("Interfaces Multimodales — Voz + Gestos")
    font_sm = pygame.font.SysFont("monospace", 16)
    font_md = pygame.font.SysFont("monospace", 22, bold=True)
    reloj   = pygame.time.Clock()

    t_cam = threading.Thread(target=hilo_camara, daemon=True)
    t_voz = threading.Thread(target=hilo_voz,    daemon=True)
    t_cam.start()
    t_voz.start()

    print("🚀 Sistema iniciado. Presiona Q para salir.")

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                estado_global["ejecutando"] = False
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_q:
                estado_global["ejecutando"] = False
                pygame.quit()
                sys.exit()

        evaluar_accion()
        dibujar_pygame(pantalla, font_sm, font_md)
        reloj.tick(FPS_OBJETIVO)
