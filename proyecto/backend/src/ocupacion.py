from __future__ import annotations

from random import Random
import time


class GeneradorOcupacion:
    """Generates random parking occupancy snapshots that remain stable for 5-second windows."""

    def __init__(self, seed: int = 23) -> None:
        self._seed = seed
        self._snapshot_bucket = None
        self._snapshot_indice_libre = None

    def obtener_indice_libre(self, total_espacios: int) -> int:
        """Returns the index of the free parking space for the current 5-second window."""

        bucket = int(time.time() // 5)

        if bucket != self._snapshot_bucket:
            rng = Random(self._seed + bucket)
            self._snapshot_indice_libre = rng.randrange(total_espacios)
            self._snapshot_bucket = bucket

        return self._snapshot_indice_libre

    def es_ocupado(self, indice: int, total_espacios: int) -> bool:
        """Returns True if the space at the given index should be occupied."""

        indice_libre = self.obtener_indice_libre(total_espacios)
        return indice != indice_libre
