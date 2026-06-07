from __future__ import annotations


class Navegador:
    """Optimal route calculator for a parking lot with two lateral entries."""

    def __init__(self, entradas: dict[str, tuple[float, float]]) -> None:
        self._entradas = entradas

    def calcular_ruta_optima(self, espacios: list, entrada: str = 'oeste') -> dict:
        """Shortest 3-waypoint route: lateral entry → central aisle → nearest free space."""

        disponibles = [e for e in espacios if not e.ocupado and not e.reservado]

        if not disponibles:
            return {'entrada': entrada, 'destino': None, 'ruta': [], 'distancia': 0}

        entrada_x, _ = self._entradas.get(entrada, next(iter(self._entradas.values())))

        mejor_espacio = None
        mejor_ruta: list = []
        mejor_distancia: float | None = None

        for espacio in disponibles:
            ruta = self._construir_ruta(entrada_x, espacio)
            distancia = self._longitud_ruta(ruta)
            if mejor_distancia is None or distancia < mejor_distancia:
                mejor_espacio = espacio
                mejor_ruta = ruta
                mejor_distancia = distancia

        return {
            'entrada': entrada,
            'destino': {
                'id': mejor_espacio.id,
                'x': mejor_espacio.x,
                'z': mejor_espacio.z,
            },
            'ruta': mejor_ruta,
            'distancia': round(mejor_distancia, 2),
        }

    def _construir_ruta(self, entrada_x: float, espacio) -> list[dict]:
        """Entry (lateral wall, Z=0) → aisle column (same X as space, Z=0) → space."""
        return [
            {'x': round(entrada_x, 3), 'z': 0.0},
            {'x': round(espacio.x, 3), 'z': 0.0},
            {'x': round(espacio.x, 3), 'z': round(espacio.z, 3)},
        ]

    def _longitud_ruta(self, ruta: list[dict]) -> float:
        total = 0.0
        for i in range(1, len(ruta)):
            dx = ruta[i]['x'] - ruta[i - 1]['x']
            dz = ruta[i]['z'] - ruta[i - 1]['z']
            total += (dx * dx + dz * dz) ** 0.5
        return total
