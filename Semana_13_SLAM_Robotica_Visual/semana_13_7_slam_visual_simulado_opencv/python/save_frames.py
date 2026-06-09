"""Regenera la secuencia sintética y guarda los 60 frames en media/frames/."""

import cv2
import numpy as np
import os

MEDIA_DIR = os.path.join(os.path.dirname(__file__), "..", "media", "frames")
os.makedirs(MEDIA_DIR, exist_ok=True)


def generate_synthetic_scene(n_points=150, img_size=480):
    rng = np.random.default_rng(42)
    pts = rng.uniform(-3, 3, (n_points, 3)).astype(np.float32)
    pts[:, 2] += 6.0
    return pts


def project_points(pts3d, R, t, K, img_size=480):
    pts_cam = (R @ pts3d.T).T + t.flatten()
    valid = pts_cam[:, 2] > 0.1
    pts_cam = pts_cam[valid]
    uvw = (K @ pts_cam.T).T
    uv = uvw[:, :2] / uvw[:, 2:3]
    in_frame = (
        (uv[:, 0] >= 0) & (uv[:, 0] < img_size) &
        (uv[:, 1] >= 0) & (uv[:, 1] < img_size)
    )
    return uv[in_frame].astype(np.float32), pts_cam[in_frame]


def render_frame(pts3d, R, t, K, img_size=480):
    img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    rng = np.random.default_rng(int(abs(t.flatten()[0]) * 1000) % 9999)
    noise = rng.integers(0, 18, img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    uv, _ = project_points(pts3d, R, t, K, img_size)
    for p in uv:
        x, y = int(p[0]), int(p[1])
        color = (int(80 + (x / img_size) * 175), int(80 + (y / img_size) * 175), 200)
        cv2.circle(img, (x, y), 4, color, -1)
        cv2.circle(img, (x, y), 6, (255, 255, 255), 1)
    return img


def build_frame_sequence(n_frames=60, img_size=480):
    K = np.array([
        [img_size * 0.8, 0,             img_size / 2],
        [0,              img_size * 0.8, img_size / 2],
        [0,              0,              1           ],
    ], dtype=np.float64)
    pts3d = generate_synthetic_scene(150, img_size)
    frames = []
    for i in range(n_frames):
        angle = (i / n_frames) * 2 * np.pi * 0.6
        cx = 1.8 * np.sin(angle)
        cy = 0.5 * np.sin(angle * 2) * 0.4
        cz = i * 0.06
        Rw = cv2.Rodrigues(np.array([0.0, angle * 0.25, 0.0]))[0]
        tw = np.array([[cx], [cy], [cz]], dtype=np.float64)
        R_cam = Rw.T
        t_cam = -Rw.T @ tw
        frames.append(render_frame(pts3d, R_cam, t_cam, K, img_size))
    return frames


frames = build_frame_sequence(n_frames=60, img_size=480)

for i, frame in enumerate(frames):
    path = os.path.join(MEDIA_DIR, f"frame_{i:02d}.png")
    cv2.imwrite(path, frame)

print(f"Guardados {len(frames)} frames en {os.path.abspath(MEDIA_DIR)}")
