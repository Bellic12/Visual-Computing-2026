from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EscalaPlano:
    """Simple conversion helper from image pixels to world units."""

    origen_px_x: float = 640.0
    origen_px_y: float = 360.0
    metros_por_pixel_x: float = 0.025
    metros_por_pixel_y: float = 0.025


def px_a_mundo(px_x: float, px_y: float, escala: EscalaPlano | None = None) -> tuple[float, float]:
    """Convert (x, y) in image pixels to (x, z) world coordinates in meters."""

    escala = escala or EscalaPlano()
    x_mundo = (px_x - escala.origen_px_x) * escala.metros_por_pixel_x
    z_mundo = (px_y - escala.origen_px_y) * escala.metros_por_pixel_y
    return round(x_mundo, 3), round(z_mundo, 3)
