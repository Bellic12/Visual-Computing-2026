from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from detector import DetectorParqueadero
from navegador import Navegador

app = FastAPI(title="Parking Detector API", version="0.1.0")

detector = DetectorParqueadero()

entradas = {
    'noroeste': (-15.0, -11.5),
    'noreste': (15.0, -11.5),
    'suroeste': (-15.0, 11.5),
    'sureste': (15.0, 11.5),
}

navegador = Navegador(entradas=entradas)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/espacios")
def get_espacios() -> list[dict[str, str | float | bool]]:
    espacios = detector.obtener_espacios()
    return [
        {
            "id": e.id,
            "x": e.x,
            "z": e.z,
            "ocupado": e.ocupado,
        }
        for e in espacios
    ]


@app.get("/estado")
def get_estado(entrada: str = "noroeste") -> dict:
    espacios = detector.obtener_espacios()
    ruta = navegador.calcular_ruta_optima(espacios, entrada=entrada)

    return {
        'entrada': ruta['entrada'],
        'espacios': [
            {
                'id': espacio.id,
                'x': espacio.x,
                'z': espacio.z,
                'ocupado': espacio.ocupado,
            }
            for espacio in espacios
        ],
        'destino': ruta['destino'],
        'ruta': ruta['ruta'],
        'distancia': ruta['distancia'],
    }


@app.get("/ruta-optima")
def get_ruta_optima(entrada: str = "noroeste") -> dict:
    espacios = detector.obtener_espacios()
    return navegador.calcular_ruta_optima(espacios, entrada=entrada)
