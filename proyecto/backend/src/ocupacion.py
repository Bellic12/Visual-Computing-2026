from __future__ import annotations

from random import Random
import time


class GeneradorOcupacion:
    """Generates random parking occupancy snapshots stable for 5-second windows.

    ~40 % of the 62 spaces are free each window, giving enough room for
    multi-car reservation testing while still looking realistically busy.
    """

    def __init__(self, seed: int = 23, tasa_ocupacion: float = 0.60) -> None:
        self._seed = seed
        self._tasa_ocupacion = tasa_ocupacion
        self._snapshot_bucket: int | None = None
        self._snapshot_ocupados: set[int] = set()

    def _renovar_snapshot(self, total_espacios: int) -> None:
        bucket = int(time.time() // 5)
        if bucket == self._snapshot_bucket:
            return
        rng = Random(self._seed + bucket)
        n_ocupados = round(total_espacios * self._tasa_ocupacion)
        self._snapshot_ocupados = set(rng.sample(range(total_espacios), n_ocupados))
        self._snapshot_bucket = bucket

    def obtener_clave_snapshot(self, total_espacios: int) -> int:
        self._renovar_snapshot(total_espacios)
        return self._snapshot_bucket  # type: ignore[return-value]

    def es_ocupado(self, indice: int, total_espacios: int) -> bool:
        self._renovar_snapshot(total_espacios)
        return indice in self._snapshot_ocupados
