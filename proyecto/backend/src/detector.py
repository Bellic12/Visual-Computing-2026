from __future__ import annotations

from dataclasses import dataclass

from homografia import px_a_mundo
from ocupacion import GeneradorOcupacion


@dataclass(frozen=True)
class Espacio:
    id: str
    x: float
    z: float
    ocupado: bool


class DetectorParqueadero:
    """Detects and interprets parking spaces from the parking lot layout and occupancy data."""

    def __init__(self, seed: int = 23, filas: int = 3, columnas: int = 6) -> None:
        self._espacios_px = self._crear_malla_px(filas=filas, columnas=columnas)
        self._generador_ocupacion = GeneradorOcupacion(seed=seed)

    def _crear_malla_px(self, filas: int, columnas: int) -> list[tuple[str, float, float]]:
        """Creates the pixel-space grid of parking spaces."""

        espacios: list[tuple[str, float, float]] = []
        base_x, base_y = 280, 150
        dx, dy = 190, 260

        for f in range(filas):
            for c in range(columnas):
                espacio_id = f"E-{f + 1}-{c + 1}"
                px_x = base_x + c * dx
                px_y = base_y + f * dy
                espacios.append((espacio_id, px_x, px_y))

        return espacios

    def obtener_espacios(self) -> list[Espacio]:
        """Returns the current state of all parking spaces."""

        return self._generar_espacios()

    def _generar_espacios(self) -> list[Espacio]:
        """Generates parking space objects with current occupancy from stable 5-second snapshots."""

        resultado = []

        for indice, (espacio_id, px_x, px_y) in enumerate(self._espacios_px):
            x, z = px_a_mundo(px_x, px_y)
            ocupado = self._generador_ocupacion.es_ocupado(indice, len(self._espacios_px))
            resultado.append(Espacio(id=espacio_id, x=x, z=z, ocupado=ocupado))

        return resultado

    def obtener_clave_snapshot(self) -> int:
        """Returns the current occupancy snapshot key."""

        return self._generador_ocupacion.obtener_clave_snapshot(len(self._espacios_px))
