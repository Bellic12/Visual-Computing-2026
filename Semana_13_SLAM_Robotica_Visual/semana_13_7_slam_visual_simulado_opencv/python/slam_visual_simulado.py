"""
Taller SLAM Visual Simulado con OpenCV
Seguimiento de trayectoria con cámara virtual usando odometría visual.
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, PillowWriter
import os

# ─── Rutas de salida ────────────────────────────────────────────────────────
MEDIA_DIR = os.path.join(os.path.dirname(__file__), "..", "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

# ─── 1. Generación de secuencia sintética ───────────────────────────────────

def generate_synthetic_scene(n_points: int = 120, img_size: int = 480) -> np.ndarray:
    """Crea una escena 3D sintética con puntos aleatorios (nubes de puntos en cubos)."""
    rng = np.random.default_rng(42)
    pts = rng.uniform(-3, 3, (n_points, 3)).astype(np.float32)
    pts[:, 2] += 6.0  # delante de la cámara
    return pts


def project_points(pts3d: np.ndarray, R: np.ndarray, t: np.ndarray,
                   K: np.ndarray, img_size: int = 480) -> tuple:
    """Proyecta puntos 3D sobre el plano imagen."""
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


def render_frame(pts3d: np.ndarray, R: np.ndarray, t: np.ndarray,
                 K: np.ndarray, img_size: int = 480) -> np.ndarray:
    """Renderiza un frame con los puntos proyectados sobre fondo oscuro."""
    img = np.zeros((img_size, img_size, 3), dtype=np.uint8)
    # Fondo con textura sutil para ayudar al detector
    rng = np.random.default_rng(int(abs(t[0, 0]) * 1000) % 9999)
    noise = rng.integers(0, 18, img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)

    uv, _ = project_points(pts3d, R, t, K, img_size)
    for p in uv:
        x, y = int(p[0]), int(p[1])
        color = (
            int(80 + (x / img_size) * 175),
            int(80 + (y / img_size) * 175),
            200,
        )
        cv2.circle(img, (x, y), 4, color, -1)
        cv2.circle(img, (x, y), 6, (255, 255, 255), 1)
    return img


def build_frame_sequence(n_frames: int = 60, img_size: int = 480):
    """
    Genera una secuencia de frames simulando una cámara que sigue una
    trayectoria circular con ligero avance en Z.
    """
    K = np.array([
        [img_size * 0.8, 0,             img_size / 2],
        [0,              img_size * 0.8, img_size / 2],
        [0,              0,              1           ],
    ], dtype=np.float64)

    pts3d = generate_synthetic_scene(150, img_size)

    frames, camera_poses = [], []
    for i in range(n_frames):
        angle = (i / n_frames) * 2 * np.pi * 0.6  # arco ~216°
        cx = 1.8 * np.sin(angle)
        cy = 0.5 * np.sin(angle * 2) * 0.4
        cz = i * 0.06

        # Pose de la cámara en el mundo
        Rw = cv2.Rodrigues(np.array([0.0, angle * 0.25, 0.0]))[0]
        tw = np.array([[cx], [cy], [cz]], dtype=np.float64)

        # Transformación mundo → cámara
        R_cam = Rw.T
        t_cam = -Rw.T @ tw

        frames.append(render_frame(pts3d, R_cam, t_cam, K, img_size))
        camera_poses.append((tw.flatten(), Rw))

    return frames, camera_poses, K


# ─── 2. Odometría visual con ORB + Essential Matrix ──────────────────────────

def visual_odometry(frames: list, K: np.ndarray):
    """
    Estima la trayectoria de la cámara cuadro a cuadro con:
      - Detector ORB
      - Emparejador BFMatcher (Hamming)
      - findEssentialMat + recoverPose
    """
    orb = cv2.ORB_create(nfeatures=1000)
    bf  = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    fx = K[0, 0]
    cx, cy = K[0, 2], K[1, 2]

    # Pose acumulada
    R_acc = np.eye(3)
    t_acc = np.zeros((3, 1))

    trajectory   = [t_acc.flatten().copy()]
    match_images = []   # frames con matches dibujados
    kp_map       = []   # puntos clave acumulados en 2D (para el mapa)

    prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
    kp_prev, des_prev = orb.detectAndCompute(prev_gray, None)

    for idx in range(1, len(frames)):
        curr_gray = cv2.cvtColor(frames[idx], cv2.COLOR_BGR2GRAY)
        kp_curr, des_curr = orb.detectAndCompute(curr_gray, None)

        if des_prev is None or des_curr is None or len(kp_prev) < 8 or len(kp_curr) < 8:
            trajectory.append(trajectory[-1].copy())
            prev_gray, kp_prev, des_prev = curr_gray, kp_curr, des_curr
            continue

        matches = bf.match(des_prev, des_curr)
        matches = sorted(matches, key=lambda m: m.distance)
        good    = matches[:min(150, len(matches))]

        if len(good) < 8:
            trajectory.append(trajectory[-1].copy())
            prev_gray, kp_prev, des_prev = curr_gray, kp_curr, des_curr
            continue

        pts1 = np.float64([kp_prev[m.queryIdx].pt for m in good])
        pts2 = np.float64([kp_curr[m.trainIdx].pt for m in good])

        E, mask_e = cv2.findEssentialMat(
            pts1, pts2,
            focal=fx, pp=(cx, cy),
            method=cv2.RANSAC, prob=0.999, threshold=1.0,
        )

        if E is None or mask_e is None:
            trajectory.append(trajectory[-1].copy())
            prev_gray, kp_prev, des_prev = curr_gray, kp_curr, des_curr
            continue

        n_inliers, R_rel, t_rel, mask_p = cv2.recoverPose(
            E, pts1, pts2, focal=fx, pp=(cx, cy), mask=mask_e.copy()
        )

        if n_inliers < 6:
            trajectory.append(trajectory[-1].copy())
            prev_gray, kp_prev, des_prev = curr_gray, kp_curr, des_curr
            continue

        # Integrar movimiento (escala unitaria)
        t_acc = t_acc + R_acc @ t_rel
        R_acc = R_rel @ R_acc

        trajectory.append(t_acc.flatten().copy())

        # Acumular puntos del mapa en 2D (X-Z)
        inlier_mask = (mask_p.ravel() > 0)
        for p in pts2[inlier_mask]:
            kp_map.append((t_acc[0, 0], t_acc[2, 0]))

        # Imagen de matches para el GIF
        match_img = cv2.drawMatches(
            frames[idx - 1], kp_prev,
            frames[idx],     kp_curr,
            good[:40], None,
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
        )
        match_images.append(match_img)

        prev_gray, kp_prev, des_prev = curr_gray, kp_curr, des_curr

    return trajectory, match_images, kp_map


# ─── 3. Guardado de medios ───────────────────────────────────────────────────

def save_match_gif(match_images: list, path: str, fps: int = 8):
    """Guarda un GIF animado con los frames de emparejamiento."""
    fig, ax = plt.subplots(figsize=(12, 4), dpi=90)
    ax.axis("off")
    im = ax.imshow(cv2.cvtColor(match_images[0], cv2.COLOR_BGR2RGB))

    def update(i):
        im.set_data(cv2.cvtColor(match_images[i], cv2.COLOR_BGR2RGB))
        ax.set_title(f"Emparejamiento ORB — Frame {i + 1}/{len(match_images)}", fontsize=11)
        return [im]

    anim = FuncAnimation(fig, update, frames=len(match_images), interval=1000 // fps, blit=True)
    anim.save(path, writer=PillowWriter(fps=fps))
    plt.close(fig)
    print(f"  GIF matches guardado: {path}")


def save_trajectory_gif(trajectory: list, gt_poses: list, path: str, fps: int = 10):
    """Guarda un GIF animado con la trayectoria estimada vs ground truth."""
    gt_x = [p[0][0] for p in gt_poses]
    gt_z = [p[0][2] for p in gt_poses]

    est_x = [p[0] for p in trajectory]
    est_z = [p[2] for p in trajectory]

    x_all = gt_x + est_x
    z_all = gt_z + est_z
    pad = 0.5
    xl = (min(x_all) - pad, max(x_all) + pad)
    zl = (min(z_all) - pad, max(z_all) + pad)

    fig, ax = plt.subplots(figsize=(7, 6), dpi=100)
    ax.set_xlim(*xl); ax.set_ylim(*zl)
    ax.set_xlabel("X (m)"); ax.set_ylabel("Z (m)")
    ax.set_title("Trayectoria SLAM Visual — Estimada vs Ground Truth")
    ax.grid(True, alpha=0.3)

    line_gt,  = ax.plot([], [], "g--", lw=2, label="Ground Truth")
    line_est, = ax.plot([], [], "b-",  lw=2, label="Estimada")
    dot_gt    = ax.scatter([], [], c="green",  s=40, zorder=5)
    dot_est   = ax.scatter([], [], c="blue",   s=40, zorder=5)
    ax.legend(loc="upper left")

    patch_start = mpatches.Patch(color="red", label="Inicio")
    ax.plot(gt_x[0], gt_z[0], "r*", ms=14)
    ax.legend(handles=[
        mpatches.Patch(color="green", label="Ground Truth"),
        mpatches.Patch(color="blue",  label="Estimada"),
        mpatches.Patch(color="red",   label="Inicio"),
    ], loc="upper left")

    def update(i):
        n = i + 1
        line_gt.set_data(gt_x[:n], gt_z[:n])
        line_est.set_data(est_x[:n], est_z[:n])
        dot_gt.set_offsets([[gt_x[i], gt_z[i]]])
        dot_est.set_offsets([[est_x[i], est_z[i]]])
        ax.set_title(f"Trayectoria SLAM Visual — Frame {n}/{len(trajectory)}")
        return line_gt, line_est, dot_gt, dot_est

    anim = FuncAnimation(fig, update, frames=len(trajectory), interval=1000 // fps, blit=True)
    anim.save(path, writer=PillowWriter(fps=fps))
    plt.close(fig)
    print(f"  GIF trayectoria guardado: {path}")


def save_map_image(trajectory: list, kp_map: list, gt_poses: list, path: str):
    """Guarda imagen estática del mapa 2D con puntos clave y trayectoria."""
    fig, ax = plt.subplots(figsize=(8, 7), dpi=120)

    if kp_map:
        mx = [p[0] for p in kp_map]
        mz = [p[1] for p in kp_map]
        ax.scatter(mx, mz, c="orange", s=6, alpha=0.35, label="Puntos del mapa")

    gt_x = [p[0][0] for p in gt_poses]
    gt_z = [p[0][2] for p in gt_poses]
    ax.plot(gt_x, gt_z, "g--", lw=2, label="Ground Truth")

    est_x = [p[0] for p in trajectory]
    est_z = [p[2] for p in trajectory]
    ax.plot(est_x, est_z, "b-", lw=2, label="Estimada")

    ax.plot(gt_x[0], gt_z[0], "r*", ms=16, label="Inicio")
    ax.plot(gt_x[-1], gt_z[-1], "rs", ms=12, label="Fin GT")
    ax.set_xlabel("X (m)"); ax.set_ylabel("Z (m)")
    ax.set_title("Mapa 2D — SLAM Visual Simulado")
    ax.legend(); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)
    print(f"  Mapa 2D guardado: {path}")


def save_keypoint_frame(frames: list, path: str):
    """Guarda imagen estática con puntos clave ORB detectados en un frame."""
    orb = cv2.ORB_create(nfeatures=1000)
    sample = frames[len(frames) // 2]
    gray = cv2.cvtColor(sample, cv2.COLOR_BGR2GRAY)
    kps, _ = orb.detectAndCompute(gray, None)
    out = cv2.drawKeypoints(
        sample, kps, None,
        flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
    )
    fig, ax = plt.subplots(figsize=(6, 6), dpi=110)
    ax.imshow(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
    ax.set_title(f"Puntos clave ORB detectados ({len(kps)} keypoints)")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=110)
    plt.close(fig)
    print(f"  Frame con keypoints guardado: {path}")


def save_trajectory_static(trajectory: list, gt_poses: list, path: str):
    """Guarda imagen estática comparando trayectoria estimada vs GT."""
    fig, ax = plt.subplots(figsize=(8, 6), dpi=120)

    gt_x = [p[0][0] for p in gt_poses]
    gt_z = [p[0][2] for p in gt_poses]
    ax.plot(gt_x, gt_z, "g--", lw=2.5, label="Ground Truth")

    est_x = [p[0] for p in trajectory]
    est_z = [p[2] for p in trajectory]
    ax.plot(est_x, est_z, "b-", lw=2.5, label="Estimada (VO)")

    ax.plot(gt_x[0], gt_z[0], "r*", ms=16, label="Inicio")
    ax.set_xlabel("X (m)"); ax.set_ylabel("Z (m)")
    ax.set_title("Comparación Trayectoria Estimada vs Ground Truth")
    ax.legend(); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)
    print(f"  Trayectoria estática guardada: {path}")


# ─── 4. Pipeline principal ───────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  SLAM Visual Simulado — Pipeline completo")
    print("=" * 60)

    # ── Paso 1: Generar secuencia sintética
    print("\n[1/5] Generando secuencia sintética de 60 frames...")
    frames, gt_poses, K = build_frame_sequence(n_frames=60, img_size=480)
    print(f"      {len(frames)} frames generados.")

    # ── Paso 2: Odometría visual
    print("\n[2/5] Ejecutando odometría visual (ORB + Essential Matrix)...")
    trajectory, match_images, kp_map = visual_odometry(frames, K)
    print(f"      Trayectoria: {len(trajectory)} poses estimadas.")
    print(f"      Matches guardados: {len(match_images)} imágenes.")

    # ── Paso 3: Guardar medios
    print("\n[3/5] Guardando medios en ../media/ ...")

    # GIF de emparejamiento
    if match_images:
        save_match_gif(
            match_images[::2],  # un frame de cada dos para aligerar el GIF
            os.path.join(MEDIA_DIR, "matches_orb.gif"),
            fps=6,
        )

    # GIF de trayectoria
    save_trajectory_gif(
        trajectory, gt_poses,
        os.path.join(MEDIA_DIR, "trayectoria_estimada.gif"),
        fps=10,
    )

    # Imágenes estáticas
    save_keypoint_frame(frames, os.path.join(MEDIA_DIR, "keypoints_orb.png"))
    save_trajectory_static(trajectory, gt_poses,
                           os.path.join(MEDIA_DIR, "trayectoria_comparacion.png"))
    save_map_image(trajectory, kp_map, gt_poses,
                   os.path.join(MEDIA_DIR, "mapa_2d.png"))

    # ── Paso 4: Métricas de error
    print("\n[4/5] Calculando error de trayectoria...")
    errors = []
    n = min(len(trajectory), len(gt_poses))
    for i in range(n):
        est = trajectory[i]
        gt  = gt_poses[i][0]
        err = np.linalg.norm(est[[0, 2]] - gt[[0, 2]])
        errors.append(err)
    print(f"      Error promedio XZ: {np.mean(errors):.4f} m")
    print(f"      Error máximo  XZ: {np.max(errors):.4f} m")

    # ── Paso 5: Gráfica de error a lo largo del tiempo
    print("\n[5/5] Guardando gráfica de error...")
    fig, ax = plt.subplots(figsize=(9, 4), dpi=110)
    ax.plot(errors, "r-", lw=1.8)
    ax.fill_between(range(len(errors)), errors, alpha=0.2, color="red")
    ax.set_xlabel("Frame"); ax.set_ylabel("Error Euclidiano XZ (m)")
    ax.set_title("Error de Trayectoria a lo Largo del Tiempo")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(MEDIA_DIR, "error_trayectoria.png"), dpi=110)
    plt.close(fig)
    print(f"  Error guardado: {os.path.join(MEDIA_DIR, 'error_trayectoria.png')}")

    print("\n" + "=" * 60)
    print("  Pipeline completado. Archivos en ../media/")
    print("=" * 60)


if __name__ == "__main__":
    main()
