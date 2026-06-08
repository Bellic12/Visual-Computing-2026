"""
3D Gaussian Splatting - Rendering Demonstration
Workshop: 3D Reconstruction - NeRF, Gaussian Splatting, SLAM
Author: Juan David Cardenas Galvis
Date: 2026-06-07

Demonstrates the core Gaussian Splatting pipeline:
  1. Scene as a set of 3D Gaussians (position, covariance, color, opacity)
  2. Each Gaussian projected to 2D screen space via perspective Jacobian
  3. Sorted back-to-front (painter's algorithm)
  4. Alpha compositing -> final RGB image
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import pathlib

np.random.seed(42)

SCRIPT_DIR = pathlib.Path(__file__).parent
MEDIA_DIR  = SCRIPT_DIR.parent / "resultados"
MEDIA_DIR.mkdir(exist_ok=True)


# ── Data structure ─────────────────────────────────────────────────────────────

class Gaussian3D:
    def __init__(self, position, color, scale, rotation=None, opacity=0.75):
        self.position = np.asarray(position, dtype=float)
        self.color    = np.clip(np.asarray(color, dtype=float), 0, 1)
        self.scale    = np.asarray(scale, dtype=float)
        self.rotation = np.eye(3) if rotation is None else np.asarray(rotation, dtype=float)
        self.opacity  = float(np.clip(opacity, 0, 1))

    def covariance_3d(self):
        S = np.diag(self.scale ** 2)
        return self.rotation @ S @ self.rotation.T

    def project(self, view_R, view_t):
        """
        Project 3D Gaussian to 2D.
        Returns (mu2d, Sigma2d, depth) where depth > 0 means in front of camera.
        """
        p_cam = view_R @ self.position + view_t

        if p_cam[2] < 0.01:          # behind camera
            return None, None, p_cam[2]

        z = p_cam[2]
        Sig3 = self.covariance_3d()

        # Jacobian of perspective division at p_cam
        J = np.array([
            [1.0 / z, 0.0,     -p_cam[0] / z ** 2],
            [0.0,     1.0 / z, -p_cam[1] / z ** 2],
        ])
        Sig2 = J @ view_R @ Sig3 @ view_R.T @ J.T

        mu2d = p_cam[:2] / z
        return mu2d, Sig2, z


# ── Renderer ──────────────────────────────────────────────────────────────────

def build_view(cam_pos, cam_target):
    """
    Build view rotation R and translation t such that:
      p_cam = R @ p_world + t
    Camera looks along +Z (in-front objects have p_cam[2] > 0).
    """
    fwd = cam_target - cam_pos
    fwd_len = np.linalg.norm(fwd)
    if fwd_len < 1e-8:
        return np.eye(3), np.zeros(3)
    fwd /= fwd_len

    world_up = np.array([0.0, 1.0, 0.0])
    right = np.cross(fwd, world_up)
    r_len = np.linalg.norm(right)
    if r_len < 1e-6:
        world_up = np.array([1.0, 0.0, 0.0])
        right = np.cross(fwd, world_up)
        r_len = np.linalg.norm(right)
    right /= r_len
    up = np.cross(right, fwd)   # corrected up

    # Camera basis rows: [right, up, fwd]  ->  p_cam[2] > 0 for objects in front
    R = np.stack([right, up, fwd], axis=0)
    t = -R @ cam_pos
    return R, t


def render(splats, cam_pos, cam_target, H=300, W=300, fov_deg=60.0):
    """Render list of Gaussian3D splats to an RGB image."""
    R, t = build_view(cam_pos, cam_target)
    focal = (W / 2.0) / np.tan(np.radians(fov_deg / 2.0))

    # Depth-sort: back-to-front (largest z first -> painter's algorithm)
    depths = [(R @ sp.position + t)[2] for sp in splats]
    order  = np.argsort(depths)[::-1]

    canvas_rgb = np.ones((H, W, 3), dtype=float)   # white background
    canvas_T   = np.ones((H, W),    dtype=float)   # remaining transmittance

    for idx in order:
        sp = splats[idx]
        mu2d, Sig2, depth = sp.project(R, t)

        if mu2d is None or depth < 0.01:
            continue

        # Screen-space pixel position
        px = mu2d[0] * focal + W / 2.0
        py = -mu2d[1] * focal + H / 2.0   # flip Y: screen y increases downward

        if px < -W or px > 2 * W or py < -H or py > 2 * H:
            continue

        # Covariance in pixel space
        Sig_px = Sig2 * focal ** 2 + np.eye(2) * 1e-4

        try:
            inv_S = np.linalg.inv(Sig_px)
        except np.linalg.LinAlgError:
            continue

        eigvals = np.clip(np.linalg.eigvalsh(Sig_px), 0, None)
        radius  = int(min(3.5 * np.sqrt(eigvals.max() + 1e-8), 80))

        x0, x1 = max(0, int(px - radius)), min(W, int(px + radius + 1))
        y0, y1 = max(0, int(py - radius)), min(H, int(py + radius + 1))

        if x1 <= x0 or y1 <= y0:
            continue

        # Per-pixel Gaussian weight
        ys, xs  = np.mgrid[y0:y1, x0:x1]
        dxy     = np.stack([xs.ravel() - px, ys.ravel() - py], axis=-1)
        mahal   = np.einsum("ni,ij,nj->n", dxy, inv_S, dxy)
        gauss   = np.exp(-0.5 * mahal).reshape(y1 - y0, x1 - x0)

        alpha   = np.clip(sp.opacity * gauss, 0, 1)
        contrib = canvas_T[y0:y1, x0:x1] * alpha   # how much this Gaussian contributes

        for c in range(3):
            # Subtract from white background: white * (1-alpha) + color * alpha
            canvas_rgb[y0:y1, x0:x1, c] -= contrib * (1.0 - sp.color[c])
        canvas_T[y0:y1, x0:x1] *= (1.0 - alpha)

    return np.clip(canvas_rgb, 0, 1)


# ── Scene construction ─────────────────────────────────────────────────────────

def build_scene():
    """Construct demo scene: red sphere, blue cube, green cylinder, yellow rings, floor."""
    splats = []

    # Red sphere (surface points)
    n = 300
    phi_s   = np.arccos(1 - 2 * np.random.rand(n))
    theta_s = np.random.rand(n) * 2 * np.pi
    r_s     = 0.30 + np.random.randn(n) * 0.012
    pts_s   = np.stack([
        r_s * np.sin(phi_s) * np.cos(theta_s),
        r_s * np.sin(phi_s) * np.sin(theta_s),
        r_s * np.cos(phi_s),
    ], axis=-1) + np.array([0.55, 0.0, 0.0])

    center_s = np.array([0.55, 0.0, 0.0])
    for pt in pts_s:
        nrm = pt - center_s
        nrm /= np.linalg.norm(nrm) + 1e-8
        col = np.clip([0.85 + 0.15 * nrm[0], 0.10 + 0.15 * abs(nrm[1]), 0.10], 0, 1)
        splats.append(Gaussian3D(pt, col, [0.04, 0.04, 0.04], opacity=0.60))

    # Blue cube (solid fill)
    n = 200
    for pt in np.random.uniform(-0.28, 0.28, (n, 3)) + np.array([-0.55, 0.0, 0.0]):
        splats.append(Gaussian3D(pt, [0.15, 0.35, 0.92], [0.05, 0.05, 0.05], opacity=0.55))

    # Green cylinder
    n   = 180
    ang = np.random.rand(n) * 2 * np.pi
    h   = np.random.uniform(-0.30, 0.30, n)
    cyl_pts = np.stack([0.18 * np.cos(ang), h, 0.18 * np.sin(ang)], axis=-1) + np.array([0.0, 0.30, 0.60])
    for pt in cyl_pts:
        splats.append(Gaussian3D(pt, [0.10, 0.82, 0.20], [0.04, 0.07, 0.04], opacity=0.62))

    # Yellow rings
    n = 160
    for ring_y in [-0.18, 0.02, 0.22]:
        ang_t  = np.random.rand(n // 3) * 2 * np.pi
        maj, mn = 0.24, 0.06
        pts_t  = np.stack([
            (maj + mn * np.cos(ang_t * 4)) * np.cos(ang_t),
            ring_y + mn * np.sin(ang_t * 4),
            (maj + mn * np.cos(ang_t * 4)) * np.sin(ang_t),
        ], axis=-1) + np.array([-0.55, 0.40, 0.60])
        for pt in pts_t:
            splats.append(Gaussian3D(pt, [0.96, 0.82, 0.10], [0.025, 0.025, 0.025], opacity=0.72))

    # Ground plane
    for fp in np.random.uniform(-1.2, 1.2, (120, 2)):
        splats.append(Gaussian3D(
            [fp[0], -0.35, fp[1]],
            [0.62 + 0.06 * np.random.rand(), 0.55 + 0.06 * np.random.rand(), 0.45],
            [0.15, 0.01, 0.15], opacity=0.38,
        ))

    return splats


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("3D Gaussian Splatting - Rendering Demonstration")
    print("=" * 60)

    scene = build_scene()
    print(f"\nScene: {len(scene)} Gaussian splats")

    # ── 1. Six-view grid ─────────────────────────────────────────────────────
    views = [
        (np.array([ 0.0, 0.4,  2.2]), np.array([0, 0, 0]), "Front"),
        (np.array([ 2.2, 0.4,  0.0]), np.array([0, 0, 0]), "Right Side"),
        (np.array([-2.2, 0.4,  0.0]), np.array([0, 0, 0]), "Left Side"),
        (np.array([ 0.0, 0.4, -2.2]), np.array([0, 0, 0]), "Back"),
        (np.array([ 1.6, 1.8,  1.6]), np.array([0, 0, 0]), "Top-Diagonal"),
        (np.array([ 0.0, 2.6,  0.1]), np.array([0, 0, 0]), "Top View"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(14, 10))
    fig.patch.set_facecolor("#0d1117")
    fig.suptitle("3D Gaussian Splatting - Novel View Synthesis\n"
                 "(Red Sphere  Blue Cube  Green Cylinder  Yellow Rings)",
                 fontsize=13, fontweight="bold", color="white")

    print("\nRendering views...")
    for idx, (cam_pos, cam_target, label) in enumerate(views):
        print(f"  [{idx+1}/6] {label}")
        img = render(scene, cam_pos, cam_target)
        ax  = axes[idx // 3][idx % 3]
        ax.imshow(img)
        ax.set_title(label, color="white", fontsize=10)
        ax.axis("off")
        ax.set_facecolor("#0d1117")

    plt.tight_layout()
    out = MEDIA_DIR / "gs_novel_views.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  OK Saved: {out}")

    # ── 2. High-resolution single render ─────────────────────────────────────
    print("  Rendering high-res (450x450)...")
    img_hq = render(scene, np.array([1.4, 0.9, 1.6]), np.array([0.0, 0.0, 0.0]), H=450, W=450)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.imshow(img_hq)
    ax.set_title("3D Gaussian Splatting - High-Quality Render", fontsize=12, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    out = MEDIA_DIR / "gs_highres_render.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  OK Saved: {out}")

    # ── 3. Concept diagrams ───────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("3D Gaussian Splatting - Core Concepts", fontsize=13, fontweight="bold")

    # (a) 2D Gaussian ellipses
    ax = axes[0]
    ax.set_title("(a) 2D Gaussian Splats (screen space)")
    np.random.seed(42)
    n_d = 18
    centers = np.random.uniform(-3.5, 3.5, (n_d, 2))
    cols    = np.random.uniform(0, 1, (n_d, 3))
    w_d, h_d = np.random.uniform(0.3, 1.2, n_d), np.random.uniform(0.2, 0.8, n_d)
    ang_d   = np.random.uniform(0, 180, n_d)
    opa_d   = np.random.uniform(0.4, 0.85, n_d)
    for i in range(n_d):
        ax.add_patch(Ellipse(xy=centers[i], width=w_d[i]*2, height=h_d[i]*2,
                              angle=ang_d[i], color=cols[i], alpha=opa_d[i]))
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
    ax.set_aspect("equal"); ax.grid(True, alpha=0.2)

    # (b) Alpha compositing
    ax = axes[1]
    ax.set_title("(b) Alpha Compositing (Back to Front)")
    x = np.linspace(0, 10, 500)
    layer_params = [
        (2.0, 0.8, [0.9, 0.3, 0.3], 0.75, "G1 (back)"),
        (4.0, 0.6, [0.3, 0.6, 1.0], 0.70, "G2"),
        (6.5, 0.5, [0.3, 0.9, 0.3], 0.65, "G3"),
        (8.0, 0.7, [0.9, 0.8, 0.2], 0.60, "G4 (front)"),
    ]
    T_c = np.ones_like(x)
    for mu, sig, col, opa, lbl in layer_params:
        g = np.exp(-0.5 * ((x - mu) / sig) ** 2)
        al = opa * g
        ax.fill_between(x, 0, T_c * al, alpha=0.6, color=col, label=lbl)
        T_c *= (1 - al)
    ax.set_xlabel("Screen coordinate x"); ax.set_ylabel("Contribution")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

    # (c) PSNR vs splat count
    ax = axes[2]
    ax.set_title("(c) PSNR vs Number of Gaussians")
    counts = [10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]
    psnr   = [12 + 6 * np.log10(max(c, 1)) for c in counts]
    ax.semilogx(counts, psnr, "b-o", linewidth=2, markersize=5)
    ax.axvline(x=len(scene), color="red", linestyle="--",
               label=f"This scene ({len(scene)} splats)")
    ax.set_xlabel("Number of Gaussians (log scale)"); ax.set_ylabel("PSNR (dB, approx.)")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = MEDIA_DIR / "gs_concepts.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  OK Saved: {out}")

    # ── 4. Scene decomposition ────────────────────────────────────────────────
    n_sphere, n_cube, n_cyl = 300, 200, 180
    subsets = [
        ("Red Sphere",      scene[:n_sphere]),
        ("Blue Cube",       scene[n_sphere:n_sphere+n_cube]),
        ("Green Cylinder",  scene[n_sphere+n_cube:n_sphere+n_cube+n_cyl]),
        ("Full Scene",      scene),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    fig.suptitle("3D Gaussian Splatting - Scene Decomposition by Object",
                 fontsize=12, fontweight="bold")

    cam_p = np.array([1.5, 0.5, 1.8])
    cam_t = np.array([0.0, 0.0, 0.0])

    for idx, (lbl, subset) in enumerate(subsets):
        print(f"  Rendering decomposition: {lbl} ({len(subset)} splats)")
        img_sub = render(subset, cam_p, cam_t, H=220, W=220)
        axes[idx].imshow(img_sub)
        axes[idx].set_title(f"{lbl}\n({len(subset)} splats)", fontsize=9)
        axes[idx].axis("off")

    plt.tight_layout()
    out = MEDIA_DIR / "gs_decomposition.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  OK Saved: {out}")

    print("\n" + "=" * 60)
    print("Gaussian Splatting done. Files saved to gaussian_splatting/resultados/")


if __name__ == "__main__":
    main()
