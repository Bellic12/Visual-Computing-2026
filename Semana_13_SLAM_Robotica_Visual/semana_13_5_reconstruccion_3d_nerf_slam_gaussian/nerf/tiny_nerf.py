"""
Tiny-NeRF: Neural Radiance Field - Volume Rendering Demonstration
Workshop: 3D Reconstruction - NeRF, Gaussian Splatting, SLAM
Author: Juan David Cardenas Galvis
Date: 2026-06-07

Demonstrates the core NeRF pipeline:
  1. Positional encoding of 3D coordinates
  2. Ray generation from camera poses
  3. Volume rendering (transmittance + alpha compositing)
  4. Novel view synthesis from analytic sphere scene
"""

import numpy as np
import matplotlib.pyplot as plt
import pathlib

np.random.seed(42)

SCRIPT_DIR = pathlib.Path(__file__).parent
MEDIA_DIR = SCRIPT_DIR / "screenshots"
MEDIA_DIR.mkdir(exist_ok=True)


# ── Positional Encoding ────────────────────────────────────────────────────────

def positional_encoding(x, L=6):
    """Fourier positional encoding: maps low-dim coords to high-freq features."""
    parts = [x]
    for k in range(L):
        parts.append(np.sin((2 ** k) * np.pi * x))
        parts.append(np.cos((2 ** k) * np.pi * x))
    return np.concatenate(parts, axis=-1)


# ── Analytic Scene: Colored Sphere ────────────────────────────────────────────

def sphere_field(pts):
    """
    Analytic density + color field representing a colored sphere.
    Returns (rgb, sigma) - the ground truth the MLP would approximate.
    """
    center = np.array([0.0, 0.0, 0.0])
    radius = 0.5

    offset = pts - center
    dist = np.linalg.norm(offset, axis=-1, keepdims=True)

    sigma = np.where(dist < radius, 80.0, 0.0)

    n = offset / (dist + 1e-8)
    r_ch = np.clip(0.55 + 0.45 * n[..., 0:1], 0, 1)
    g_ch = np.clip(0.55 + 0.45 * n[..., 1:2], 0, 1)
    b_ch = np.clip(0.55 - 0.45 * n[..., 2:3], 0, 1)
    rgb = np.concatenate([r_ch, g_ch, b_ch], axis=-1)

    return rgb.reshape(-1, 3), sigma.reshape(-1, 1)


# ── Camera Utilities ───────────────────────────────────────────────────────────

def look_at(cam_pos, target=np.zeros(3), up=np.array([0, 1, 0])):
    """Build a camera-to-world matrix (c2w) for given pose."""
    fwd = target - cam_pos
    fwd = fwd / (np.linalg.norm(fwd) + 1e-8)
    right = np.cross(fwd, up)
    right = right / (np.linalg.norm(right) + 1e-8)
    up_corrected = np.cross(right, fwd)

    c2w = np.eye(4)
    c2w[:3, 0] = right
    c2w[:3, 1] = up_corrected
    c2w[:3, 2] = -fwd
    c2w[:3, 3] = cam_pos
    return c2w


def pose_spherical(theta_deg, phi_deg, radius=2.0):
    """Camera on a sphere around origin; theta = azimuth, phi = elevation."""
    theta = np.radians(theta_deg)
    phi = np.radians(phi_deg)
    cam_pos = radius * np.array([
        np.cos(phi) * np.sin(theta),
        np.sin(phi),
        np.cos(phi) * np.cos(theta),
    ])
    return look_at(cam_pos)


def get_rays(H, W, focal, c2w):
    """Generate per-pixel ray origins and directions in world space."""
    j, i = np.meshgrid(np.arange(H), np.arange(W), indexing='ij')
    dirs = np.stack([
        (i - W * 0.5) / focal,
        -(j - H * 0.5) / focal,
        -np.ones_like(i),
    ], axis=-1)

    rays_d = (dirs[..., None, :] * c2w[:3, :3]).sum(-1)
    rays_o = np.broadcast_to(c2w[:3, 3], rays_d.shape)
    return rays_o.reshape(-1, 3), rays_d.reshape(-1, 3)


# ── Volume Rendering ───────────────────────────────────────────────────────────

def volume_render(rgb_samples, sigma_samples, t_vals, rays_d):
    """
    Classic NeRF volume rendering integral (discrete approximation).

    C(r) = Sum T_i * (1 - exp(-sigma_i * delta_i)) * c_i
    T_i  = exp(-Sum_{j<i} sigma_j * delta_j)
    """
    deltas = t_vals[..., 1:] - t_vals[..., :-1]
    deltas = np.concatenate([deltas, np.full(deltas[..., :1].shape, 1e10)], axis=-1)
    ray_len = np.linalg.norm(rays_d, axis=-1, keepdims=True)
    deltas = deltas * ray_len

    alpha = 1.0 - np.exp(-sigma_samples[..., 0] * deltas)

    T = np.cumprod(
        np.concatenate([np.ones((*alpha.shape[:-1], 1)), 1 - alpha + 1e-10], axis=-1),
        axis=-1,
    )[..., :-1]

    weights = T * alpha
    rgb_map   = (weights[..., None] * rgb_samples).sum(-2)
    depth_map = (weights * t_vals).sum(-1)
    acc_map   = weights.sum(-1)

    return rgb_map, depth_map, acc_map, weights


# ── Render a Single View ───────────────────────────────────────────────────────

def render_view(theta, phi, H=80, W=80, near=1.0, far=3.0, n_samples=96):
    """Render the analytic sphere scene from (theta, phi) camera angle."""
    focal = 0.8 * W
    c2w = pose_spherical(theta, phi)

    rays_o, rays_d = get_rays(H, W, focal, c2w)
    rays_d_unit = rays_d / (np.linalg.norm(rays_d, axis=-1, keepdims=True) + 1e-8)

    t_vals = np.linspace(near, far, n_samples)
    t_vals = np.broadcast_to(t_vals, (len(rays_o), n_samples)).copy()

    pts = rays_o[:, None, :] + t_vals[:, :, None] * rays_d_unit[:, None, :]
    pts_flat = pts.reshape(-1, 3)

    rgb_flat, sigma_flat = sphere_field(pts_flat)

    rgb_samp   = rgb_flat.reshape(len(rays_o), n_samples, 3)
    sigma_samp = sigma_flat.reshape(len(rays_o), n_samples, 1)

    rgb_map, depth_map, acc_map, _ = volume_render(rgb_samp, sigma_samp, t_vals, rays_d_unit)

    rgb_img = rgb_map + (1 - acc_map[..., None])
    return np.clip(rgb_img.reshape(H, W, 3), 0, 1), depth_map.reshape(H, W)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Tiny-NeRF: Volume Rendering Demonstration")
    print("=" * 60)

    views = [
        (0,   20, "Front"),
        (60,  20, "Right-45"),
        (120, 20, "Right-120"),
        (180, 20, "Back"),
        (0,   60, "Top Angle"),
        (90, -10, "Low Angle"),
    ]

    # ── 1. Novel view synthesis grid ──────────────────────────────────────────
    fig, axes = plt.subplots(2, 3, figsize=(13, 9))
    fig.patch.set_facecolor("#1a1a2e")
    fig.suptitle("Tiny-NeRF - Novel View Synthesis\n(Volume-rendered colored sphere scene)",
                 fontsize=14, fontweight="bold", color="white")

    print("\nRendering novel views...")
    renders = []
    for idx, (theta, phi, name) in enumerate(views):
        print(f"  [{idx+1}/6] theta={theta:>4}deg  phi={phi:>4}deg  -> {name}")
        rgb, depth = render_view(theta, phi)
        renders.append((rgb, depth, name, theta, phi))

        ax = axes[idx // 3][idx % 3]
        ax.imshow(rgb)
        ax.set_title(f"{name}  theta={theta}deg, phi={phi}deg", color="white", fontsize=9)
        ax.axis("off")
        ax.set_facecolor("#1a1a2e")

    plt.tight_layout()
    out = MEDIA_DIR / "nerf_novel_views.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  OK Saved: {out}")

    # ── 2. Depth maps ─────────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 3, figsize=(13, 9))
    fig.patch.set_facecolor("#1a1a2e")
    fig.suptitle("Tiny-NeRF - Depth Maps (Volume Rendering)",
                 fontsize=14, fontweight="bold", color="white")

    for idx, (rgb, depth, name, theta, phi) in enumerate(renders):
        ax = axes[idx // 3][idx % 3]
        im = ax.imshow(depth, cmap="plasma")
        ax.set_title(f"Depth: {name}", color="white", fontsize=9)
        ax.axis("off")
        plt.colorbar(im, ax=ax, fraction=0.046, label="t (world units)")

    plt.tight_layout()
    out = MEDIA_DIR / "nerf_depth_maps.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  OK Saved: {out}")

    # ── 3. Positional encoding visualization ─────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(16, 4))
    fig.suptitle("NeRF - Positional Encoding: Why High Frequencies Matter",
                 fontsize=12, fontweight="bold")

    x = np.linspace(-1, 1, 300)
    for ax_idx, L in enumerate([1, 3, 6]):
        ax = axes[ax_idx]
        colors = plt.cm.rainbow(np.linspace(0, 1, L))
        for k in range(L):
            ax.plot(x, np.sin((2 ** k) * np.pi * x),
                    color=colors[k], alpha=0.8, linewidth=1.5, label=f"sin(2^{k}*pi*x)")
        ax.set_title(f"L = {L}  ({3*(1+2*L)} total features for xyz)")
        ax.set_xlabel("Input coordinate")
        ax.set_ylabel("Encoded value")
        ax.legend(fontsize=7, loc="upper right")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = MEDIA_DIR / "nerf_positional_encoding.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  OK Saved: {out}")

    # ── 4. Volume rendering equation diagram ─────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("NeRF - Volume Rendering Equation  C(r) = Sum Ti*ai*ci",
                 fontsize=12, fontweight="bold")

    t = np.linspace(1.0, 3.5, 200)
    sigma_demo = (np.exp(-((t - 1.9) ** 2) / 0.04) * 25
                  + np.exp(-((t - 2.8) ** 2) / 0.02) * 15)
    dt_demo  = t[1] - t[0]
    alpha_d  = 1 - np.exp(-sigma_demo * dt_demo)
    T_d      = np.cumprod(np.concatenate([[1.0], 1 - alpha_d[:-1] + 1e-10]))
    weights_d = T_d * alpha_d

    axes[0].fill_between(t, sigma_demo / sigma_demo.max(), alpha=0.4, color="steelblue", label="sigma(t) density")
    axes[0].plot(t, weights_d / (weights_d.max() + 1e-8),
                 color="orange", linewidth=2, label="w(t) = T*alpha weights")
    axes[0].set_xlabel("t  (distance along ray)")
    axes[0].set_ylabel("Normalized value")
    axes[0].set_title("Two surfaces along a ray")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    color_demo = np.stack([
        0.8 * np.exp(-((t - 1.9) ** 2) / 0.05) + 0.1,
        0.5 * np.exp(-((t - 2.8) ** 2) / 0.04) + 0.2,
        0.3 * np.ones_like(t),
    ], axis=-1)
    C_accum = np.cumsum(weights_d[:, None] * color_demo, axis=0)
    final_C = (weights_d[:, None] * color_demo).sum(0)

    for ch, col, lbl in zip(range(3), ["red", "green", "blue"], ["R", "G", "B"]):
        axes[1].plot(t, C_accum[:, ch], color=col, linewidth=1.5, label=f"{lbl} accumulation")
        axes[1].axhline(y=final_C[ch], color=col, linestyle="--", alpha=0.5, linewidth=1)

    axes[1].set_xlabel("t  (distance along ray)")
    axes[1].set_ylabel("C(r) accumulated color")
    axes[1].set_title("Color accumulation - dashed lines = final pixel color")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    out = MEDIA_DIR / "nerf_volume_rendering.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  OK Saved: {out}")

    print("\n" + "=" * 60)
    print("NeRF done. Files saved to nerf/screenshots/")


if __name__ == "__main__":
    main()
