from __future__ import annotations

from dataclasses import dataclass
import time

# from ocupacion import GeneradorOcupacion

from detector_real import DetectorReal
from asignador_espacios import AsignadorEspacios

# Mirror the exact geometry constants from Parqueadero3D.jsx so backend
# coordinates and frontend 3D positions are always in sync.
_STALL_W = 2.4
_STALL_D = 4.5
_LAMP_GAP = 1.6
_LOT_W = 76.0
_LOT_H = 13.5
_OX = -_LOT_W / 2          # −38.0  (world x of lot's left edge)
_OZ = -_LOT_H / 2          # −6.75  (world z of lot's top edge)
_ROW1_Z = _STALL_D / 2 + _OZ                              # −4.5
_ROW2_Z = _STALL_D * 1.5 + (_LOT_H - 2 * _STALL_D) + _OZ  # +4.5
_RIGHT_X_START = 14 * _STALL_W + _LAMP_GAP               # 35.2


@dataclass(frozen=True)
class Espacio:
    id: str
    x: float
    z: float
    ocupado: bool
    reservado: bool = False


class DetectorParqueadero:
    """62-space lot in world coordinates — matches the frontend static layout."""

    # def __init__(self, seed: int = 23) -> None:
    #     self._espacios_base = self._crear_malla()
    #     self._generador_ocupacion = GeneradorOcupacion(seed=seed)

    def __init__(self) -> None:
        self._espacios_base = self._crear_malla()
        self._detector_real = DetectorReal()
        self._ultimo_estado = None
        self._ultimo_timestamp = 0
        self._cache_segundos = 5
        self._asignador = AsignadorEspacios(
            self._espacios_base
        )
    
    def _actualizar_estado(self):
        vehiculos = self._detector_real.obtener_vehiculos()

        ocupados = self._asignador.obtener_ocupados(
            vehiculos
        )

        snapshot = hash(
            tuple(sorted(ocupados))
        )

        self._ultimo_estado = {
            "vehiculos": vehiculos,
            "ocupados": ocupados,
            "snapshot": snapshot
        }

        self._ultimo_timestamp = time.time()
    
    def _obtener_estado_cacheado(self):
        ahora = time.time()

        if (
            self._ultimo_estado is None
            or
            ahora - self._ultimo_timestamp > self._cache_segundos
        ):
            self._actualizar_estado()

        return self._ultimo_estado

    def _crear_malla(self) -> list[tuple[str, float, float]]:
        espacios: list[tuple[str, float, float]] = []
        for row in (1, 2):
            z = _ROW1_Z if row == 1 else _ROW2_Z
            for col in range(1, 15):
                x = (col - 1) * _STALL_W + _STALL_W / 2 + _OX
                espacios.append((f'E-{row}-{col}', round(x, 3), round(z, 3)))
            for col in range(15, 32):
                x = _RIGHT_X_START + (col - 15) * _STALL_W + _STALL_W / 2 + _OX
                espacios.append((f'E-{row}-{col}', round(x, 3), round(z, 3)))
        return espacios

    def obtener_espacios(self, reservados: set[str] | None = None) -> list[Espacio]:
        return self._generar_espacios(reservados or set())

    # def _generar_espacios(self, reservados: set[str]) -> list[Espacio]:
    #     resultado = []
    #     for indice, (espacio_id, x, z) in enumerate(self._espacios_base):
    #         ocupado = self._generador_ocupacion.es_ocupado(indice, len(self._espacios_base))
    #         reservado = espacio_id in reservados
    #         resultado.append(Espacio(id=espacio_id, x=x, z=z, ocupado=ocupado, reservado=reservado))
    #     return resultado

    # def _generar_espacios(self, reservados):
    #     vehiculos = self._detector_real.obtener_vehiculos()
    #     ocupados = self._asignador.obtener_ocupados(
    #         vehiculos
    #     )
    #     print("\nVEHICULOS:")
    #     for v in vehiculos:
    #         print(v)

    #     print("\nESPACIOS OCUPADOS:")
    #     for e in sorted(ocupados):
    #         print(e)
    #     resultado = []
    #     for espacio_id, x, z in self._espacios_base:
    #         resultado.append(
    #             Espacio(
    #                 id=espacio_id,
    #                 x=x,
    #                 z=z,
    #                 ocupado=espacio_id in ocupados,
    #                 reservado=espacio_id in reservados
    #             )
    #         )
    #     return resultado

    def _generar_espacios(self, reservados):
        estado = self._obtener_estado_cacheado()
        ocupados = estado["ocupados"]
        resultado = []
        for espacio_id, x, z in self._espacios_base:
            resultado.append(
                Espacio(
                    id=espacio_id,
                    x=x,
                    z=z,
                    ocupado=espacio_id in ocupados,
                    reservado=espacio_id in reservados
                )
            )

        return resultado
    
    # def obtener_clave_snapshot(self) -> int:
    #     return self._generador_ocupacion.obtener_clave_snapshot(len(self._espacios_base))

    # def obtener_clave_snapshot(self):
    #     vehiculos = self._detector_real.obtener_vehiculos()

    #     return hash(
    #         tuple(
    #             sorted(vehiculos)
    #         )
    #     )
    
    def obtener_clave_snapshot(self):
        estado = self._obtener_estado_cacheado()
        return estado["snapshot"]
        
    def obtener_estado(self):
        return self._obtener_estado_cacheado()
   