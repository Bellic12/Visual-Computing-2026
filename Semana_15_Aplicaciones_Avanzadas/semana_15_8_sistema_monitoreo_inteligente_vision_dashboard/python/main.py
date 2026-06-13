from ultralytics import YOLO
from collections import Counter
from datetime import datetime

import customtkinter as ctk
import cv2
import csv
import os
import time

from PIL import Image, ImageTk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

os.makedirs("logs", exist_ok=True)
os.makedirs("capturas", exist_ok=True)

CSV_FILE = "logs/eventos.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["timestamp", "evento", "cantidad_personas", "imagen"]
        )


class DetectorDashboard:

    def __init__(self):

        self.model = YOLO("yolov8n.pt")
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")

        self.last_detection = 0
        self.cooldown = 5

        self.total_events = 0
        self.last_event = "Ninguno"

        self.person_history = []
        self.max_points = 50

        self.app = ctk.CTk()
        self.app.title("YOLO Smart Monitor")
        self.app.geometry("1600x900")

        self.build_ui()

        self.app.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        self.update()
        self.app.mainloop()

    def build_ui(self):

        self.app.grid_columnconfigure(1,weight=1)
        self.app.grid_rowconfigure(0,weight=1)

        self.sidebar = ctk.CTkFrame(self.app,width=320,corner_radius=0)
        self.sidebar.grid(row=0,column=0,sticky="ns")

        self.main_frame = ctk.CTkFrame(self.app,corner_radius=0)
        self.main_frame.grid(row=0,column=1,sticky="nsew")
        self.main_frame.grid_rowconfigure(0,weight=4)
        self.main_frame.grid_rowconfigure(1,weight=1)
        self.main_frame.grid_columnconfigure(0,weight=1)


        # self.title_label = ctk.CTkLabel(
        #     self.sidebar,
        #     text="YOLO MONITOR",
        #     font=ctk.CTkFont(size=28,weight="bold")
        # )
        # self.title_label.pack(pady=(30, 20))


        self.status_card = ctk.CTkFrame(self.sidebar)
        self.status_card.pack(fill="x",padx=15,pady=10)
        ctk.CTkLabel(self.status_card,text="Estado").pack(pady=(10, 0))

        self.status_label = ctk.CTkLabel(
            self.status_card,
            text="INACTIVO",
            text_color="green",
            font=ctk.CTkFont(size=24,weight="bold")
        )
        self.status_label.pack(pady=(5, 10))


        self.people_card = ctk.CTkFrame(self.sidebar)
        self.people_card.pack(fill="x",padx=15,pady=10)
        ctk.CTkLabel(self.people_card,text="Personas Detectadas").pack(pady=(10, 0))

        self.person_label = ctk.CTkLabel(
            self.people_card,
            text="0",
            font=ctk.CTkFont(size=42,weight="bold")
        )
        self.person_label.pack(pady=(5, 10))


        self.events_card = ctk.CTkFrame(self.sidebar)
        self.events_card.pack(fill="x",padx=15,pady=10)
        ctk.CTkLabel(self.events_card,text="Eventos Registrados").pack(pady=(10, 0))

        self.events_label = ctk.CTkLabel(
            self.events_card,
            text="0",
            font=ctk.CTkFont(size=32,weight="bold")
        )
        self.events_label.pack(pady=(5, 10))


        self.last_event_card = ctk.CTkFrame(self.sidebar)
        self.last_event_card.pack(fill="x",padx=15,pady=10)
        ctk.CTkLabel(self.last_event_card,text="Último Evento").pack(pady=(10, 0))

        self.last_event_label = ctk.CTkLabel(
            self.last_event_card,
            text="Ninguno",
            wraplength=250,
            justify="left"
        )
        self.last_event_label.pack(pady=(5, 10))


        self.objects_card = ctk.CTkFrame(self.sidebar)
        self.objects_card.pack(fill="both",expand=True,padx=15,pady=10)
        ctk.CTkLabel(self.objects_card,text="Objetos Detectados").pack(pady=(10, 5))

        self.objects_box = ctk.CTkTextbox(self.objects_card,height=250)
        self.objects_box.pack(fill="both",expand=True,padx=10,pady=(0, 10))


        self.video_container = ctk.CTkFrame(self.main_frame)
        self.video_container.grid(row=0,column=0,sticky="nsew",padx=10,pady=(10, 5))

        self.video_label = ctk.CTkLabel(self.video_container,text="")
        self.video_label.pack(fill="both",expand=True,padx=10,pady=10)


        self.graph_container = ctk.CTkFrame(self.main_frame)
        self.graph_container.grid(row=1,column=0,sticky="nsew",padx=10,pady=(5, 10))

        self.figure = Figure(figsize=(10, 2),dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure,master=self.graph_container)
        self.canvas.get_tk_widget().pack(fill="both",expand=True)

    def save_event(self, frame, people_count):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = (f"capturas/persona_{timestamp}.jpg")
        cv2.imwrite(image_path,frame)

        with open(CSV_FILE,"a",newline="",encoding="utf-8") as f:

            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                "Persona detectada",
                people_count,
                image_path
            ])

        self.total_events += 1

        self.last_event = (
            f"{timestamp}\n"
            f"{people_count} persona(s)"
        )

    def update_stats(self, counter):

        people = counter.get("person",0)

        if people > 0:
            self.status_label.configure(text="ALERTA",text_color="#ff5555")
        else:
            self.status_label.configure(text="INACTIVO",text_color="#50fa7b")

        self.person_label.configure(text=str(people))
        self.events_label.configure(text=str(self.total_events))
        self.last_event_label.configure(text=self.last_event)
        self.objects_box.delete("0.0","end")

        for obj, qty in sorted(counter.items(),key=lambda x: x[1],reverse=True):
            self.objects_box.insert("end",f"{obj:<20} {qty}\n")

    def update_graph(self, people_count):

        self.person_history.append(people_count)

        if len(self.person_history) > self.max_points:
            self.person_history.pop(0)

        self.ax.clear()
        self.ax.plot(self.person_history,linewidth=2)
        self.ax.set_title("Personas Detectadas")
        self.ax.grid(alpha=0.3)
        self.canvas.draw()

    def update(self):

        ret, frame = self.cap.read()

        if not ret:
            self.app.after(10,self.update)
            return

        results = self.model.predict(frame,imgsz=640,verbose=False)
        rendered = results[0].plot()
        boxes = results[0].boxes
        class_ids = (boxes.cls.cpu().numpy().astype(int) if len(boxes) > 0 else [])

        names = self.model.names
        detected = [names[i] for i in class_ids]
        counter = Counter(detected)
        people_count = counter.get("person",0)

        now = time.time()

        if (people_count > 0 and now - self.last_detection > self.cooldown):

            self.save_event(frame,people_count)
            self.last_detection = now
            print(f"[ALERTA] {people_count} persona(s)")

        self.update_stats(counter)
        self.update_graph(people_count)

        rgb = cv2.cvtColor(rendered,cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)

        width = self.video_container.winfo_width()
        height = self.video_container.winfo_height()

        if width > 100 and height > 100:
            image = image.resize((width - 20, height - 20))

        photo = ImageTk.PhotoImage(image=image)
        self.video_label.configure(image=photo)
        self.video_label.image = photo
        self.app.after(30,self.update)

    def on_close(self):

        self.cap.release()
        cv2.destroyAllWindows()
        self.app.destroy()


if __name__ == "__main__":
    DetectorDashboard()