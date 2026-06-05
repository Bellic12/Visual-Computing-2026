from __future__ import annotations

import time
from threading import Lock


class GestorReservas:
    """Thread-safe manager for temporary parking space reservations."""

    TIMEOUT_SEGUNDOS = 60

    def __init__(self) -> None:
        self._reservas: dict[str, dict] = {}
        self._lock = Lock()
        self._version = 0

    @property
    def version(self) -> int:
        return self._version

    def reservar(self, espacio_id: str, entrada: str) -> bool:
        """Marks a space as reserved. Returns False if already reserved."""
        with self._lock:
            self._limpiar_expiradas()
            if espacio_id in self._reservas:
                return False
            self._reservas[espacio_id] = {
                'entrada': entrada,
                'timestamp': time.time(),
            }
            self._version += 1
            return True

    def liberar(self, espacio_id: str) -> None:
        with self._lock:
            if espacio_id in self._reservas:
                del self._reservas[espacio_id]
                self._version += 1

    def esta_reservado(self, espacio_id: str) -> bool:
        with self._lock:
            self._limpiar_expiradas()
            return espacio_id in self._reservas

    def obtener_reservados(self) -> set[str]:
        with self._lock:
            self._limpiar_expiradas()
            return set(self._reservas.keys())

    def reset(self) -> None:
        with self._lock:
            self._reservas.clear()
            self._version += 1

    def _limpiar_expiradas(self) -> None:
        ahora = time.time()
        expiradas = [k for k, v in self._reservas.items() if ahora - v['timestamp'] > self.TIMEOUT_SEGUNDOS]
        for k in expiradas:
            del self._reservas[k]
            self._version += 1
