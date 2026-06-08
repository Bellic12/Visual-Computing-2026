"""
2D EKF-SLAM: Extended Kalman Filter SLAM Demonstration
Workshop: 3D Reconstruction - NeRF, Gaussian Splatting, SLAM
Author: Juan David Cardenas Galvis
Date: 2026-06-07

Implements full EKF-SLAM:
  - Unicycle robot motion model with odometry noise
  - Range-bearing landmark observations with sensor noise
  - EKF predict + update loop
  - Visualization of trajectory, landmarks, and uncertainty ellipses
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Ellipse
import pathlib

np.random.seed(7)

SCRIPT_DIR = pathlib.Path(__file__).parent
MEDIA_DIR  = SCRIPT_DIR.parent / "mapas"
MEDIA_DIR.mkdir(exist_ok=True)


# ── Motion model (unicycle) ────────────────────────────────────────────────────

def motion_step(state, u, dt=0.1):
    x, y, th = state
    v, w = u
    if abs(w) < 1e-6:
        return np.array([x + v * np.cos(th) * dt,
                         y + v * np.sin(th) * dt,
                         wrap(th)])
    r = v / w
    return np.array([x + r * (-np.sin(th) + np.sin(th + w * dt)),
                     y + r * ( np.cos(th) - np.cos(th + w * dt)),
                     wrap(th + w * dt)])


def motion_jac(state, u, dt=0.1):
    _, _, th = state
    v, w = u
    if abs(w) < 1e-6:
        return np.array([[1, 0, -v * np.sin(th) * dt],
                         [0, 1,  v * np.cos(th) * dt],
                         [0, 0,  1]])
    r = v / w
    return np.array([[1, 0, r * (-np.cos(th) + np.cos(th + w * dt))],
                     [0, 1, r * (-np.sin(th) + np.sin(th + w * dt))],
                     [0, 0, 1]])


# ── Observation model (range-bearing) ─────────────────────────────────────────

def observe(robot, lm):
    dx, dy = lm[0] - robot[0], lm[1] - robot[1]
    return np.array([np.sqrt(dx**2 + dy**2), wrap(np.arctan2(dy, dx) - robot[2])])


def obs_jac(robot, lm):
    dx, dy = lm[0] - robot[0], lm[1] - robot[1]
    r2 = dx**2 + dy**2;  r = np.sqrt(r2)
    Hr = np.array([[-dx/r, -dy/r,  0.0],
                   [ dy/r2, -dx/r2, -1.0]])
    Hl = np.array([[ dx/r,  dy/r],
                   [-dy/r2, dx/r2]])
    return Hr, Hl


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


# ── EKF-SLAM ──────────────────────────────────────────────────────────────────

class EKF_SLAM:
    def __init__(self, n_lm, Q, R):
        self.n_lm = n_lm
        self.Q    = Q
        self.R    = R
        self.dim  = 3 + 2 * n_lm
        self.mu   = np.zeros(self.dim)
        self.Sigma = np.eye(self.dim) * 1e6
        self.Sigma[:3, :3] = np.zeros((3, 3))
        self.seen = np.zeros(n_lm, dtype=bool)

    @property
    def robot(self):
        return self.mu[:3]

    def lm_pos(self, i):
        return self.mu[3 + 2*i : 3 + 2*i + 2]

    def lm_cov(self, i):
        s = 3 + 2*i;  return self.Sigma[s:s+2, s:s+2]

    def predict(self, u, dt=0.1):
        F = np.eye(self.dim)
        F[:3, :3] = motion_jac(self.robot, u, dt)
        self.mu[:3] = motion_step(self.robot, u, dt)
        Q_full = np.zeros((self.dim, self.dim));  Q_full[:3, :3] = self.Q
        self.Sigma = F @ self.Sigma @ F.T + Q_full

    def update(self, z, lm_id):
        s = 3 + 2 * lm_id
        if not self.seen[lm_id]:
            r, phi = z;  th = self.robot[2]
            self.mu[s]   = self.robot[0] + r * np.cos(th + phi)
            self.mu[s+1] = self.robot[1] + r * np.sin(th + phi)
            self.seen[lm_id] = True
            return
        Hr, Hl = obs_jac(self.robot, self.lm_pos(lm_id))
        H = np.zeros((2, self.dim))
        H[:, :3] = Hr;  H[:, s:s+2] = Hl
        innov    = z - observe(self.robot, self.lm_pos(lm_id))
        innov[1] = wrap(innov[1])
        K = self.Sigma @ H.T @ np.linalg.inv(H @ self.Sigma @ H.T + self.R)
        self.mu += K @ innov
        self.mu[2] = wrap(self.mu[2])
        self.Sigma = (np.eye(self.dim) - K @ H) @ self.Sigma


# ── Simulation ─────────────────────────────────────────────────────────────────

def simulate():
    true_lm = np.array([
        [ 3.5,  2.0], [-2.5,  3.5], [ 4.5, -1.5],
        [-3.0, -2.5], [ 1.5,  4.5], [ 3.0, -3.5],
        [-1.5, -4.5], [ 5.0,  1.0], [-4.5,  0.5],
        [ 0.5, -4.0], [ 2.0,  2.5], [-2.0,  0.0],
    ])
    n_lm = len(true_lm)

    N = 300
    t_seq = np.linspace(0, 4 * np.pi, N)
    controls = np.column_stack([
        0.35 * np.ones(N),
        0.18 * np.sin(t_seq * 0.4) + 0.04 * np.cos(t_seq * 1.1),
    ])

    Q = np.diag([0.008, 0.008, 0.003]) ** 2
    R = np.diag([0.12, 0.05]) ** 2
    OBS_RANGE = 3.5

    ekf        = EKF_SLAM(n_lm, Q, R)
    true_pose  = np.zeros(3)
    true_traj  = [true_pose.copy()]
    est_traj   = [ekf.robot.copy()]

    for u in controls:
        true_pose  = motion_step(true_pose, u) + np.random.multivariate_normal([0]*3, Q)
        true_pose[2] = wrap(true_pose[2])
        ekf.predict(u)
        for li, lm in enumerate(true_lm):
            if np.linalg.norm(lm - true_pose[:2]) < OBS_RANGE:
                z = observe(true_pose, lm) + np.random.multivariate_normal([0]*2, R)
                ekf.update(z, li)
        true_traj.append(true_pose.copy())
        est_traj.append(ekf.robot.copy())

    return np.array(true_traj), np.array(est_traj), true_lm, ekf


# ── Helpers ────────────────────────────────────────────────────────────────────

def draw_ellipse(ax, mean, cov, n_std=2.0, **kw):
    vals, vecs = np.linalg.eigh(cov)
    vals  = np.maximum(vals, 0)
    angle = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
    w, h  = 2 * n_std * np.sqrt(vals)
    ax.add_patch(Ellipse(xy=mean, width=w, height=h, angle=angle, **kw))


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("2D EKF-SLAM Demonstration")
    print("=" * 60)
    print("\nRunning simulation...")
    true_traj, est_traj, true_lm, ekf = simulate()
    n_lm = len(true_lm)
    print(f"  {len(true_traj)} steps, {n_lm} landmarks")

    lm_errs = [np.linalg.norm(true_lm[i] - ekf.lm_pos(i))
               for i in range(n_lm) if ekf.seen[i]]
    pos_err = np.sqrt(np.sum((true_traj[:, :2] - est_traj[:, :2])**2, axis=1))

    bounds = (-7.5, 6.5, -6.5, 6.5)

    # ── 1. Map + trajectory ───────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("EKF-SLAM - Simultaneous Localization and Mapping",
                 fontsize=14, fontweight="bold")

    for ax, title in zip(axes, ["Ground Truth", "EKF Estimate"]):
        ax.set_title(title, fontweight="bold", fontsize=12)
        ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)")
        ax.set_xlim(*bounds[:2]); ax.set_ylim(*bounds[2:])
        ax.set_aspect("equal"); ax.grid(True, alpha=0.3, linestyle="--")

    axes[0].plot(true_traj[:, 0], true_traj[:, 1], "b-", lw=1.5, alpha=0.7, label="True path")
    axes[0].scatter(*true_traj[0, :2],  color="limegreen", s=100, zorder=7, label="Start")
    axes[0].scatter(*true_traj[-1, :2], color="red",       s=100, zorder=7, marker="s", label="End")
    for i, lm in enumerate(true_lm):
        axes[0].scatter(*lm, marker="*", color="gold", s=220, edgecolors="darkorange", lw=0.6, zorder=6)
        axes[0].text(lm[0]+0.15, lm[1]+0.1, f"L{i}", fontsize=7, color="#b8860b")
    axes[0].legend(fontsize=9, loc="upper right")

    axes[1].plot(true_traj[:, 0], true_traj[:, 1], "b-", lw=0.8, alpha=0.22, label="True path")
    axes[1].plot(est_traj[:, 0],  est_traj[:, 1],  "b--", lw=1.5, alpha=0.7, label="EKF path")
    axes[1].scatter(*est_traj[0, :2],  color="limegreen", s=100, zorder=7, label="Start")
    axes[1].scatter(*est_traj[-1, :2], color="red",       s=100, zorder=7, marker="s", label="End")

    for i in range(n_lm):
        if ekf.seen[i]:
            draw_ellipse(axes[1], ekf.lm_pos(i), ekf.lm_cov(i),
                         facecolor="khaki", edgecolor="darkorange", alpha=0.45, lw=1.2)
            axes[1].scatter(*ekf.lm_pos(i), marker="*", color="gold", s=200,
                            edgecolors="darkorange", lw=0.6, zorder=6)
            axes[1].scatter(*true_lm[i], marker="x", color="crimson", s=50, zorder=5, lw=1.5)
            axes[1].annotate("", xy=true_lm[i], xytext=ekf.lm_pos(i),
                             arrowprops=dict(arrowstyle="->", color="crimson", alpha=0.25, lw=0.8))

    extra = [mpatches.Patch(facecolor="khaki",   edgecolor="darkorange", label="EKF lm + 2-sigma ellipse"),
             mpatches.Patch(color="crimson",      alpha=0.6,              label="True lm (x)")]
    axes[1].legend(handles=list(axes[1].get_legend_handles_labels()[0]) + extra, fontsize=8, loc="upper right")

    plt.tight_layout()
    out = MEDIA_DIR / "slam_map_trajectory.png"
    plt.savefig(out, dpi=150, bbox_inches="tight");  plt.close()
    print(f"  OK Saved: {out}")

    # ── 2. Error analysis ─────────────────────────────────────────────────────
    head_err = np.degrees(np.abs([wrap(t - e) for t, e in zip(true_traj[:, 2], est_traj[:, 2])]))

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("EKF-SLAM - Performance Analysis", fontsize=13, fontweight="bold")

    axes[0, 0].plot(pos_err, color="crimson", lw=1.5)
    axes[0, 0].fill_between(range(len(pos_err)), pos_err, alpha=0.15, color="crimson")
    axes[0, 0].axhline(y=pos_err.mean(), color="navy", linestyle="--",
                        label=f"Mean = {pos_err.mean():.3f} m")
    axes[0, 0].set_title("Robot Position Error"); axes[0, 0].set_xlabel("Step"); axes[0, 0].set_ylabel("Error (m)")
    axes[0, 0].legend(); axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(true_traj[:, 0], true_traj[:, 1], "b-", lw=2, label="Ground truth")
    axes[0, 1].plot(est_traj[:, 0],  est_traj[:, 1],  "r--", lw=1.5, label="EKF estimate")
    axes[0, 1].set_title("Trajectory Comparison"); axes[0, 1].set_aspect("equal")
    axes[0, 1].set_xlabel("X (m)"); axes[0, 1].set_ylabel("Y (m)")
    axes[0, 1].legend(); axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(head_err, color="darkorange", lw=1.5)
    axes[1, 0].fill_between(range(len(head_err)), head_err, alpha=0.15, color="darkorange")
    axes[1, 0].axhline(y=head_err.mean(), color="navy", linestyle="--",
                        label=f"Mean = {head_err.mean():.2f} deg")
    axes[1, 0].set_title("Robot Heading Error"); axes[1, 0].set_xlabel("Step"); axes[1, 0].set_ylabel("Error (deg)")
    axes[1, 0].legend(); axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].bar(range(len(lm_errs)), lm_errs, color="steelblue", edgecolor="navy", alpha=0.8)
    axes[1, 1].axhline(y=np.mean(lm_errs), color="red", linestyle="--",
                        label=f"Mean: {np.mean(lm_errs):.3f} m")
    axes[1, 1].set_title(f"Landmark Position Errors (mean={np.mean(lm_errs):.3f} m)")
    axes[1, 1].set_xlabel("Landmark ID"); axes[1, 1].set_ylabel("Error (m)")
    axes[1, 1].legend(); axes[1, 1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    out = MEDIA_DIR / "slam_error_analysis.png"
    plt.savefig(out, dpi=150, bbox_inches="tight");  plt.close()
    print(f"  OK Saved: {out}")

    # ── 3. Map-building progression ───────────────────────────────────────────
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    fig.suptitle("EKF-SLAM - Map Building Over Time", fontsize=13, fontweight="bold")

    for ax, frac in zip(axes, [0.10, 0.25, 0.60, 1.00]):
        k = int(frac * (len(true_traj) - 1))
        ax.set_title(f"{int(frac*100)}% complete (step {k})", fontweight="bold")
        ax.plot(true_traj[:k, 0], true_traj[:k, 1], "b-", lw=1.5, alpha=0.6)
        ax.scatter(*true_traj[k, :2], color="orange", s=80, zorder=6, marker="^")
        ax.scatter(*true_traj[0, :2], color="limegreen", s=80, zorder=6)
        ax.scatter(true_lm[:, 0], true_lm[:, 1], marker="*", color="gold", s=150,
                   edgecolors="darkorange", lw=0.6, zorder=5, alpha=0.5)
        ax.set_xlim(*bounds[:2]); ax.set_ylim(*bounds[2:])
        ax.set_aspect("equal"); ax.grid(True, alpha=0.3, linestyle="--")
        ax.set_xlabel("X (m)"); ax.set_ylabel("Y (m)")

    plt.tight_layout()
    out = MEDIA_DIR / "slam_building_map.png"
    plt.savefig(out, dpi=150, bbox_inches="tight");  plt.close()
    print(f"  OK Saved: {out}")

    print("\n" + "=" * 60)
    print(f"SLAM done. Final pos error: {np.linalg.norm(true_traj[-1,:2]-est_traj[-1,:2]):.3f} m")
    print(f"           Landmark errors: mean={np.mean(lm_errs):.4f} m, max={np.max(lm_errs):.4f} m")
    print("Files saved to slam/mapas/")


if __name__ == "__main__":
    main()
