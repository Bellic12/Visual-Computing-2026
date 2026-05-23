import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import (
    load_image_rgb, save_and_display, overlay_masks,
    compute_mask_area, compute_mask_perimeter, compute_mask_centroid,
    INPUT_DIR, get_device
)


def compute_iou(m1, m2):
    intersection = np.logical_and(m1 > 0, m2 > 0).sum()
    union = np.logical_or(m1 > 0, m2 > 0).sum()
    return intersection / union if union > 0 else 0


def non_max_suppression(masks, scores, iou_threshold=0.7, score_threshold=0.85):
    flat_scores = scores.flatten()
    sorted_idxs = np.argsort(flat_scores)[::-1]
    keep = []
    for idx in sorted_idxs:
        if flat_scores[idx] < score_threshold:
            continue
        keep_iou = True
        for k in keep:
            if compute_iou(masks[idx], masks[k]) > iou_threshold:
                keep_iou = False
                break
        if keep_iou:
            keep.append(idx)
    return keep


def generate_auto_masks(model, processor, image_rgb, device, grid_size=16):
    h, w = image_rgb.shape[:2]
    xs = np.linspace(w // (2 * grid_size), w - w // (2 * grid_size), grid_size)
    ys = np.linspace(h // (2 * grid_size), h - h // (2 * grid_size), grid_size)
    grid_points = [[float(x), float(y)] for y in ys for x in xs]

    all_masks = []
    all_scores = []
    batch_size = 64

    for start in range(0, len(grid_points), batch_size):
        batch_pts = grid_points[start:start + batch_size]
        labels = [1] * len(batch_pts)
        inputs = processor(
            image_rgb,
            input_points=[batch_pts],
            input_labels=[labels],
            return_tensors="pt"
        ).to(device)

        with torch.no_grad():
            outputs = model(**inputs)

        masks = processor.image_processor.post_process_masks(
            outputs.pred_masks.cpu(),
            inputs["original_sizes"].cpu(),
            inputs["reshaped_input_sizes"].cpu()
        )[0]

        scores = outputs.iou_scores.cpu().numpy()[0]
        all_masks.append(masks.numpy())
        all_scores.append(scores)

    all_masks = np.concatenate(all_masks, axis=0)
    all_scores = np.concatenate(all_scores, axis=0)

    B, C, H, W = all_masks.shape
    all_masks = all_masks.reshape(B * C, H, W)
    all_masks = (all_masks > 0).astype(np.uint8)

    keep = non_max_suppression(all_masks, all_scores)
    print(f"    Puntos generados: {len(grid_points)}, "
          f"mascaras tras NMS: {len(keep)}")

    return all_masks[keep], all_scores.flatten()[keep]


def plot_all_masks(image_rgb, masks, scores, stem, max_display=20):
    n = min(len(masks), max_display)
    cols = min(5, n)
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
    axes = axes.flatten() if rows * cols > 1 else [axes]

    for i in range(n):
        axes[i].imshow(masks[i], cmap='gray')
        axes[i].set_title(f'Mask {i+1}\nscore={scores[i]:.3f}')
        axes[i].axis('off')

    for i in range(n, len(axes)):
        axes[i].axis('off')

    fig.suptitle(f'SAM - {n} mascaras individuales (top por score)', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'02_sam_auto_{stem}_individual_masks.png')


def plot_composite(image_rgb, masks, scores, stem):
    colors = np.random.randint(0, 255, (len(masks), 3), dtype=np.uint8)
    overlay = overlay_masks(image_rgb, masks, colors, alpha=0.4)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].imshow(image_rgb)
    axes[0].set_title('Imagen original')
    axes[0].axis('off')

    axes[1].imshow(overlay)
    axes[1].set_title(f'SAM - {len(masks)} mascaras detectadas')
    axes[1].axis('off')

    score_hist = axes[2]
    score_hist.hist(scores, bins=20, color='steelblue', edgecolor='white')
    score_hist.set_xlabel('IoU prediction score')
    score_hist.set_ylabel('Frecuencia')
    score_hist.set_title('Distribucion de scores')
    score_hist.grid(alpha=0.3)

    fig.suptitle(f'SAM - Segmentacion Automatica: {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'02_sam_auto_{stem}_composite.png')


def plot_metrics_summary(masks, scores, stem):
    areas = [compute_mask_area(m) for m in masks]
    perims = [compute_mask_perimeter(m) for m in masks]
    centroids = [compute_mask_centroid(m) for m in masks]
    valid_centroids = [c for c in centroids if c is not None]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes[0, 0].hist(areas, bins=20, color='coral', edgecolor='white')
    axes[0, 0].set_xlabel('Area (pixeles)')
    axes[0, 0].set_ylabel('Frecuencia')
    axes[0, 0].set_title('Distribucion de areas')
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].hist(perims, bins=20, color='seagreen', edgecolor='white')
    axes[0, 1].set_xlabel('Perimetro (pixeles)')
    axes[0, 1].set_ylabel('Frecuencia')
    axes[0, 1].set_title('Distribucion de perimetros')
    axes[0, 1].grid(alpha=0.3)

    if valid_centroids:
        xs = [c[0] for c in valid_centroids]
        ys = [c[1] for c in valid_centroids]
        axes[1, 0].scatter(xs, ys, c='purple', alpha=0.5, s=20)
        axes[1, 0].set_xlabel('Coordenada X')
        axes[1, 0].set_ylabel('Coordenada Y')
        axes[1, 0].set_title('Centroides de mascaras')
        axes[1, 0].grid(alpha=0.3)
        axes[1, 0].set_aspect('equal')
    else:
        axes[1, 0].text(0.5, 0.5, 'Sin centroides validos',
                        ha='center', va='center')

    stats_text = (f"Total mascaras: {len(masks)}\n"
                  f"Score medio: {np.mean(scores):.3f}\n"
                  f"Score max: {np.max(scores):.3f}\n"
                  f"Area media: {np.mean(areas):.0f} px\n"
                  f"Perimetro medio: {np.mean(perims):.1f} px")
    axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, va='center',
                    fontfamily='monospace')
    axes[1, 1].axis('off')
    axes[1, 1].set_title('Estadisticas resumen')

    fig.suptitle(f'Metricas de segmentacion SAM - {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'02_sam_auto_{stem}_metrics.png')


def main():
    print("=== SAM: Segmentacion Automatica ===")
    device = get_device()
    print(f"Dispositivo: {device}")

    from transformers import SamModel, SamProcessor
    print("Cargando modelo SAM (facebook/sam-vit-base)...")
    model = SamModel.from_pretrained("facebook/sam-vit-base").to(device)
    processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
    model.eval()
    print("Modelo cargado.")

    image_files = sorted(INPUT_DIR.glob('*.jpg')) + sorted(INPUT_DIR.glob('*.png'))
    if not image_files:
        print("No se encontraron imagenes. Ejecuta download_images.py primero.")
        return

    for i, img_path in enumerate(image_files[:4]):
        print(f"\n[{i+1}/{len(image_files)}] Procesando: {img_path.name}")
        image_rgb = load_image_rgb(img_path)
        h_img, w_img = image_rgb.shape[:2]
        scale = 640 / max(h_img, w_img)
        if scale < 1:
            new_size = (int(w_img * scale), int(h_img * scale))
            image_rgb_small = np.array(
                Image.fromarray(image_rgb).resize(new_size, Image.LANCZOS))
        else:
            image_rgb_small = image_rgb

        masks, scores = generate_auto_masks(
            model, processor, image_rgb_small, device, grid_size=16
        )

        if len(masks) == 0:
            print("  No se generaron mascaras.")
            continue

        import cv2
        masks_resized = []
        for m in masks:
            m_resized = cv2.resize(m.astype(np.float32),
                                    (w_img, h_img),
                                    interpolation=cv2.INTER_NEAREST)
            masks_resized.append((m_resized > 0).astype(np.uint8))
        masks_resized = np.array(masks_resized)

        stem = img_path.stem
        plot_all_masks(image_rgb, masks_resized, scores, stem, max_display=20)
        plot_composite(image_rgb, masks_resized, scores, stem)
        plot_metrics_summary(masks_resized, scores, stem)
        print(f"  Resultados guardados para {stem}.")

    print("\n=== SAM automatico completado ===")


from PIL import Image
if __name__ == '__main__':
    main()
