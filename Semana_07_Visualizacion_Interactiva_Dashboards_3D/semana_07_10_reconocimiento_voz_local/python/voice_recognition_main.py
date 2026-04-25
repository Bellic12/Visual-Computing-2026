"""
Taller - Voz al Código: Comandos por Reconocimiento de Voz Local
Reconocimiento de voz usando CMU Sphinx con síntesis de voz y visualización en tkinter
Autores: Juan David Buitrago Salazar, Juan David Cardenas Galvis, 
         Nicolás Rodríguez Piraban, Camilo Andres Medina Sanchez, 
         Juan Felipe Fajardo Garzón
Fecha: Abril 2026
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
from collections import deque
import tkinter as tk
from tkinter import Canvas
import random
import sounddevice as sd
import numpy as np

# Inicializar motor de síntesis de voz
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Velocidad de habla
engine.setProperty('volume', 0.9)  # Volumen

# Diccionario de comandos disponibles
COMANDOS = {
    'rojo': {'color': '#FF0000', 'rgb': (255, 0, 0)},
    'azul': {'color': '#0000FF', 'rgb': (0, 0, 255)},
    'verde': {'color': '#00FF00', 'rgb': (0, 255, 0)},
    'amarillo': {'color': '#FFFF00', 'rgb': (255, 255, 0)},
    'girar': {'action': 'rotate'},
    'iniciar': {'action': 'start'},
    'detener': {'action': 'stop'}
}

# Variables de estado
comando_detectado = None
es_escuchando = True
historial_comandos = deque(maxlen=10)
sistema_activo = True
en_rotacion = False
offset_rotacion = 0  # Para animación de rotación

# Variables para la GUI
app_window = None
canvas = None
color_actual = '#808080'  # Gris por defecto
ultima_visualizacion = "Sistema iniciado"


def hablar(texto):
    """Reproduce síntesis de voz con el texto proporcionado"""
    print(f"🔊 Bot: {texto}")
    try:
        engine.say(texto)
        engine.runAndWait()
    except Exception as e:
        print(f"⚠️  Síntesis de voz no disponible: {e}")


def actualizar_visualizacion(comando, params):
    """Actualiza la visualización en tkinter"""
    global color_actual, ultima_visualizacion, en_rotacion
    
    if 'color' in params:
        color_actual = params['color']
        ultima_visualizacion = f"Color: {comando.upper()}"
        en_rotacion = False
    elif 'action' in params:
        accion = params['action']
        if accion == 'rotate':
            en_rotacion = not en_rotacion
            ultima_visualizacion = "ROTANDO" if en_rotacion else "Rotación detenida"
        elif accion == 'start':
            global sistema_activo
            sistema_activo = True
            en_rotacion = False
            color_actual = '#808080'
            ultima_visualizacion = "✓ Sistema INICIADO"
        elif accion == 'stop':
            sistema_activo = False
            en_rotacion = False
            color_actual = '#404040'
            ultima_visualizacion = "● Sistema DETENIDO"


def procesar_comando(texto_reconocido):
    """Procesa el texto reconocido y ejecuta acciones correspondientes"""
    global comando_detectado
    
    texto_lower = texto_reconocido.lower().strip()
    print(f"\n🎤 Texto reconocido: '{texto_lower}'")
    
    # Buscar coincidencias con comandos (con mejor detección)
    comando_encontrado = None
    for comando, params in COMANDOS.items():
        # Buscar en cualquier parte del texto o como palabra completa
        if comando in texto_lower or texto_lower.startswith(comando):
            comando_encontrado = comando
            comando_detectado = comando
            historial_comandos.append(comando)
            
            # Procesar comando
            print(f"✅ Comando detectado: {comando}")
            hablar(f"Comando: {comando}")
            actualizar_visualizacion(comando, params)
            
            # Retroalimentación adicional
            if 'color' in params:
                print(f"🎨 Color: {comando.upper()}")
            elif 'action' in params:
                print(f"⚙️  Acción: {params['action'].upper()}")
            break
    
    if not comando_encontrado:
        print(f"❌ Comando no reconocido en: {texto_lower}")
        hablar("No entendí. Repite por favor")


def dibujar_interfaz():
    """Dibuja la interfaz gráfica en tkinter"""
    global canvas, color_actual, ultima_visualizacion, offset_rotacion
    
    if canvas is None or not es_escuchando:
        return
    
    try:
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # Fondo
        canvas.create_rectangle(0, 0, width, height, fill='#1E1E1E', outline='')
        
        if sistema_activo:
            # Dibujar círculo principal
            centro_x, centro_y = width // 2, height // 2
            radio = 80
            
            # Efecto de rotación - anillos animados
            if en_rotacion:
                # Incrementar offset para animación
                offset_rotacion += 5
                
                # Dibujar anillos pulsantes
                distancia_anillo1 = 40 + int(10 * abs(np.sin(np.radians(offset_rotacion))))
                distancia_anillo2 = 60 + int(15 * abs(np.cos(np.radians(offset_rotacion))))
                
                canvas.create_oval(
                    centro_x - radio - distancia_anillo1, centro_y - radio - distancia_anillo1,
                    centro_x + radio + distancia_anillo1, centro_y + radio + distancia_anillo1,
                    outline=color_actual, width=3
                )
                canvas.create_oval(
                    centro_x - radio - distancia_anillo2, centro_y - radio - distancia_anillo2,
                    centro_x + radio + distancia_anillo2, centro_y + radio + distancia_anillo2,
                    outline=color_actual, width=2
                )
            
            # Círculo principal
            canvas.create_oval(
                centro_x - radio, centro_y - radio,
                centro_x + radio, centro_y + radio,
                fill=color_actual, outline='white', width=3
            )
            
            # Texto del centro
            canvas.create_text(
                centro_x, centro_y,
                text="VOZ",
                fill='white',
                font=('Arial', 20, 'bold')
            )
        else:
            # Sistema inactivo
            canvas.create_text(
                width // 2, height // 2,
                text="SISTEMA\nINACTIVO",
                fill='#666666',
                font=('Arial', 40, 'bold'),
                justify='center'
            )
        
        # Panel de información
        info_y = 20
        canvas.create_text(
            20, info_y,
            text=f"📝 Último comando: {ultima_visualizacion}",
            fill='white',
            font=('Arial', 12),
            anchor='nw'
        )
        
        canvas.create_text(
            20, info_y + 25,
            text=f"🔴 Escuchando: {'Sí' if es_escuchando else 'No'}",
            fill='#00FF00' if es_escuchando else '#FF0000',
            font=('Arial', 12),
            anchor='nw'
        )
        
        # Instrucciones abajo
        canvas.create_text(
            20, height - 120,
            text="Comandos:\n🎨 Colores: rojo, azul, verde, amarillo\n⚙️ Acciones: girar, iniciar, detener",
            fill='#888888',
            font=('Arial', 11),
            anchor='nw'
        )
        
        canvas.after(100, dibujar_interfaz)
    except Exception as e:
        print(f"Error dibujando: {e}")
        canvas.after(100, dibujar_interfaz)


def crear_interfaz_tkinter():
    """Crea la interfaz gráfica con tkinter"""
    global app_window, canvas
    
    app_window = tk.Tk()
    app_window.title("Taller Voz al Código - Visualización en Vivo")
    app_window.geometry("900x700")
    app_window.configure(bg='#1E1E1E')
    
    # Canvas para dibujar
    canvas = Canvas(app_window, bg='#1E1E1E', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Iniciar dibujo
    dibujar_interfaz()
    
    # Manejar cierre de ventana
    def on_closing():
        global es_escuchando
        print("\n✋ Ventana cerrada por el usuario")
        es_escuchando = False
        app_window.destroy()
    
    app_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    return app_window


def reconocer_voz():
    """
    Captura audio del micrófono usando sounddevice y reconoce voz usando Google Speech API
    """
    recognizer = sr.Recognizer()
    SAMPLE_RATE = 16000  # Tasa de muestreo
    CHUNK_DURATION = 6  # segundos de grabación
    
    try:
        print("🚀 Iniciando reconocimiento de voz...")
        hablar("Sistema iniciado. Escuchando comandos.")
        print("\n📋 Comandos disponibles:")
        print("  • Colores: rojo, azul, verde, amarillo")
        print("  • Acciones: girar, iniciar, detener")
        print("\n🎙️  Listo en 3 segundos...")
        time.sleep(3)
        
        while es_escuchando:
            try:
                print("\n🔴 Escuchando...")
                
                # Capturar audio usando sounddevice
                try:
                    audio_data = sd.rec(int(SAMPLE_RATE * CHUNK_DURATION), 
                                       samplerate=SAMPLE_RATE, 
                                       channels=1, 
                                       dtype=np.float32,
                                       blocking=True)
                    
                    # Normalizar audio (convertir a rango correcto para sr.AudioData)
                    audio_int16 = np.int16(audio_data * 32767)
                    audio_bytes = audio_int16.tobytes()
                    
                    # Crear objeto AudioData para SpeechRecognition
                    audio = sr.AudioData(audio_bytes, SAMPLE_RATE, 2)
                    
                    print("⏳ Procesando...")
                    
                    # Reconocer usando Google Speech API
                    try:
                        texto = recognizer.recognize_google(audio, language='es-ES')
                        if texto.strip():
                            procesar_comando(texto)
                    except sr.UnknownValueError:
                        print("❌ Audio no entendido")
                    except sr.RequestError as e:
                        print(f"❌ Error API: {str(e)[:50]}")
                    
                except Exception as e:
                    print(f"❌ Error capturando: {e}")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error en bucle: {e}")
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Deteniendo sistema...")
        hablar("Sistema detenido")
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        hablar("Error en el sistema")


def mostrar_menu():
    """Muestra menú interactivo"""
    print("\n" + "="*60)
    print("  TALLER - VOZ AL CÓDIGO: RECONOCIMIENTO VOICE LOCAL")
    print("="*60)
    print("Autores:")
    print("  • Juan David Buitrago Salazar")
    print("  • Juan David Cardenas Galvis")
    print("  • Nicolás Rodríguez Piraban")
    print("  • Camilo Andres Medina Sanchez")
    print("  • Juan Felipe Fajardo Garzón")
    print("="*60)
    print("\n📝 INSTRUCCIONES:")
    print("1. Se abrirá una ventana con la visualización")
    print("2. Habla los comandos claramente")
    print("3. Los comandos se reconocerán y visualizarán en vivo")
    print("4. Presiona Ctrl+C o cierra la ventana para detener\n")


def main():
    """Función principal"""
    global es_escuchando, app_window
    
    mostrar_menu()
    
    # Crear interfaz gráfica
    app_window = crear_interfaz_tkinter()
    
    try:
        # Iniciar reconocimiento en un thread
        reconocimiento_thread = threading.Thread(target=reconocer_voz, daemon=True)
        reconocimiento_thread.start()
        
        # Mantener el programa activo con la ventana
        app_window.mainloop()
    
    except KeyboardInterrupt:
        print("\n✋ Programa finalizado por el usuario")
        es_escuchando = False
    except Exception as e:
        print(f"❌ Error: {e}")
        es_escuchando = False


if __name__ == "__main__":
    main()
