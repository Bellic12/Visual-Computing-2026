from __future__ import annotations


class Navegador:
    """Computes optimal routes through parking lot corridors."""

    def __init__(self, entradas: dict[str, tuple[float, float]]) -> None:
        self._entradas = entradas

    def calcular_ruta_optima(self, espacios: list, entrada: str = 'noroeste') -> dict:
        """Calculates the shortest route from entrance to the nearest free parking space."""

        disponibles = [espacio for espacio in espacios if not espacio.ocupado]

        if not disponibles:
            return {
                'entrada': entrada,
                'destino': None,
                'ruta': [],
                'distancia': 0,
            }

        entrada_x, entrada_z = self._entradas.get(entrada, self._entradas.get('noroeste', (0, 0)))
        carril_lateral_x = min(espacio.x for espacio in espacios) - 3.0

        mejor_espacio = None
        mejor_ruta = []
        mejor_distancia = None

        for espacio in disponibles:
            ruta = self._construir_ruta(
                entrada_x=entrada_x,
                entrada_z=entrada_z,
                carril_lateral_x=carril_lateral_x,
                espacio=espacio,
                entrada=entrada,
            )
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

    def _construir_ruta(self, entrada_x, entrada_z, carril_lateral_x, espacio, entrada):
        margen_pasillo = 2.45
        if entrada == 'sur':
            carril_frontal_z = round(espacio.z + margen_pasillo, 3)
        else:
            carril_frontal_z = round(espacio.z - margen_pasillo, 3)

        punto_entrada = {'x': round(entrada_x, 3), 'z': round(entrada_z, 3)}
        punto_lateral = {'x': round(carril_lateral_x, 3), 'z': round(entrada_z, 3)}
        punto_frontal = {'x': round(carril_lateral_x, 3), 'z': carril_frontal_z}
        punto_acceso = {'x': round(espacio.x, 3), 'z': carril_frontal_z}
        punto_destino = {'x': espacio.x, 'z': espacio.z}

        return [punto_entrada, punto_lateral, punto_frontal, punto_acceso, punto_destino]

    def _longitud_ruta(self, ruta):
        total = 0

        for indice in range(1, len(ruta)):
            actual = ruta[indice]
            anterior = ruta[indice - 1]
            dx = actual['x'] - anterior['x']
            dz = actual['z'] - anterior['z']
            total += (dx * dx + dz * dz) ** 0.5

        return total
