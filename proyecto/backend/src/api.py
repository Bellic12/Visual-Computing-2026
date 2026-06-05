from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from detector import DetectorParqueadero
from navegador import Navegador
from reservas import GestorReservas

app = FastAPI(title="Parking Detector API", version="0.2.0")

detector = DetectorParqueadero()
gestor_reservas = GestorReservas()

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


def construir_estado(entrada: str = "noroeste") -> dict:
    reservados = gestor_reservas.obtener_reservados()
    espacios = detector.obtener_espacios(reservados)
    ruta = navegador.calcular_ruta_optima(espacios, entrada=entrada)

    return {
        'entrada': ruta['entrada'],
        'snapshot': detector.obtener_clave_snapshot(),
        'version_reservas': gestor_reservas.version,
        'espacios': [
            {
                'id': espacio.id,
                'x': espacio.x,
                'z': espacio.z,
                'ocupado': espacio.ocupado,
                'reservado': espacio.reservado,
            }
            for espacio in espacios
        ],
        'destino': ruta['destino'],
        'ruta': ruta['ruta'],
        'distancia': ruta['distancia'],
    }


@app.get("/espacios")
def get_espacios() -> list[dict]:
    reservados = gestor_reservas.obtener_reservados()
    espacios = detector.obtener_espacios(reservados)
    return [
        {
            "id": e.id,
            "x": e.x,
            "z": e.z,
            "ocupado": e.ocupado,
            "reservado": e.reservado,
        }
        for e in espacios
    ]


@app.get("/estado")
def get_estado(entrada: str = "noroeste") -> dict:
    return construir_estado(entrada)


@app.get("/suscripcion/estado")
async def suscripcion_estado(entrada: str = "noroeste") -> StreamingResponse:
    async def generar_eventos():
        ultimo_snapshot = None
        ultima_version_reservas = None

        while True:
            estado = construir_estado(entrada)
            snapshot = estado['snapshot']
            version_reservas = estado['version_reservas']

            if snapshot != ultimo_snapshot or version_reservas != ultima_version_reservas:
                yield f"event: estado\ndata: {json.dumps(estado)}\n\n"
                ultimo_snapshot = snapshot
                ultima_version_reservas = version_reservas

            await asyncio.sleep(1)

    return StreamingResponse(generar_eventos(), media_type="text/event-stream")


@app.post("/reservar")
def post_reservar(entrada: str = "noroeste") -> dict:
    """Assigns and reserves the nearest free space from the given entrance."""
    reservados = gestor_reservas.obtener_reservados()
    espacios = detector.obtener_espacios(reservados)
    ruta = navegador.calcular_ruta_optima(espacios, entrada=entrada)

    if not ruta['destino']:
        raise HTTPException(status_code=409, detail="No hay espacios disponibles")

    espacio_id = ruta['destino']['id']
    exito = gestor_reservas.reservar(espacio_id, entrada)

    if not exito:
        raise HTTPException(status_code=409, detail="Espacio ya fue reservado, intente de nuevo")

    return {
        "ok": True,
        "espacio_id": espacio_id,
        "destino": ruta['destino'],
        "ruta": ruta['ruta'],
        "distancia": ruta['distancia'],
        "entrada": entrada,
    }


@app.delete("/reservar/{espacio_id}")
def delete_reservar(espacio_id: str) -> dict:
    """Releases a reservation (called when the car has parked)."""
    gestor_reservas.liberar(espacio_id)
    return {"ok": True}


@app.get("/ruta-optima")
def get_ruta_optima(entrada: str = "noroeste") -> dict:
    reservados = gestor_reservas.obtener_reservados()
    espacios = detector.obtener_espacios(reservados)
    return navegador.calcular_ruta_optima(espacios, entrada=entrada)
