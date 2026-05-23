import torch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import Normalize
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import (
    load_image_rgb, save_and_display, overlay_masks,
    compute_mask_area, compute_mask_perimeter, compute_mask_centroid,
    compute_bbox, compute_bbox_aspect_ratio, compute_coverage_pct,
    compute_compactness, compute_circularity, compute_iou,
    enhanced_nms, filter_background_masks, filter_pipeline,
    INPUT_DIR, OUTPUT_DIR, get_device
)
from PIL import Image


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

    print(f"    Puntos generados: {len(grid_points)}, "
          f"mascaras crudas (x3 multimask): {len(all_masks)}")

    return all_masks, all_scores.flatten()




def compute_all_metrics(masks, img_shape):
    metrics = []
    for i, m in enumerate(masks):
        area = compute_mask_area(m)
        perim = compute_mask_perimeter(m)
        cent = compute_mask_centroid(m)
        bbox = compute_bbox(m)
        ratio = compute_bbox_aspect_ratio(m)
        cov = compute_coverage_pct(m)
        comp = compute_compactness(m)
        circ = compute_circularity(m)
        metrics.append({
            'idx': i,
            'area': area,
            'perimeter': perim,
            'centroid': cent,
            'bbox': bbox,
            'aspect_ratio': ratio,
            'coverage_pct': cov,
            'compactness': comp,
            'circularity': circ,
        })
    return metrics


def plot_comprehensive_analysis(image_rgb, masks, scores, metrics, stem, img_h, img_w):
    n = len(masks)
    colors = plt.cm.tab20(np.linspace(0, 1, max(n, 1)))[:, :3] * 255
    colors = colors.astype(np.uint8)

    fig = plt.figure(figsize=(22, 14))
    gs = fig.add_gridspec(2, 4, hspace=0.3, wspace=0.3)

    ax_orig = fig.add_subplot(gs[0, 0])
    ax_overlay = fig.add_subplot(gs[0, 1])
    ax_heatmap = fig.add_subplot(gs[0, 2])
    ax_iou = fig.add_subplot(gs[0, 3])
    ax_hist_area = fig.add_subplot(gs[1, 0])
    ax_hist_ratio = fig.add_subplot(gs[1, 1])
    ax_centroid = fig.add_subplot(gs[1, 2])
    ax_summary = fig.add_subplot(gs[1, 3])

    ax_orig.imshow(image_rgb)
    ax_orig.set_title('Imagen original', fontsize=12)
    ax_orig.axis('off')

    overlay = overlay_masks(image_rgb, masks, colors, alpha=0.45)
    ax_overlay.imshow(overlay)
    ax_overlay.set_title(f'SAM - {n} mascaras filtradas', fontsize=12)
    ax_overlay.axis('off')
    for i, m in enumerate(masks):
        bbox = compute_bbox(m)
        if bbox is None:
            continue
        x1, y1, x2, y2 = bbox
        c = colors[i % len(colors)] / 255.0
        rect = Rectangle((x1, y1), x2 - x1, y2 - y1,
                         linewidth=1.5, edgecolor=c, facecolor='none', linestyle='--')
        ax_overlay.add_patch(rect)
        cx, cy = metrics[i]['centroid']
        ax_overlay.plot(cx, cy, marker='x', markersize=8, color=c, mew=2)
        ax_overlay.text(cx + 5, cy - 5, f'{i}', fontsize=8,
                        color=c, weight='bold')

    coverage_map = np.zeros((img_h, img_w), dtype=np.float32)
    for m in masks:
        coverage_map += m.astype(np.float32)
    coverage_map = coverage_map / max(n, 1)
    im_h = ax_heatmap.imshow(coverage_map, cmap='hot', vmin=0, vmax=1)
    ax_heatmap.set_title('Mapa de cobertura', fontsize=12)
    ax_heatmap.axis('off')
    plt.colorbar(im_h, ax=ax_heatmap, fraction=0.046, pad=0.04, label='Frecuencia')

    if n > 1:
        iou_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                iou_matrix[i, j] = compute_iou(masks[i], masks[j])
        im_iou = ax_iou.imshow(iou_matrix, cmap='viridis', vmin=0, vmax=1)
        ax_iou.set_title('Matriz IoU entre mascaras', fontsize=12)
        ax_iou.set_xlabel('Mascara')
        ax_iou.set_ylabel('Mascara')
        for i in range(n):
            for j in range(n):
                val = iou_matrix[i, j]
                if val > 0.3:
                    ax_iou.text(j, i, f'{val:.2f}', ha='center', va='center',
                                fontsize=6, color='white')
        plt.colorbar(im_iou, ax=ax_iou, fraction=0.046, pad=0.04, label='IoU')
    else:
        ax_iou.text(0.5, 0.5, 'Solo 1 mascara\n(sin matriz)',
                    ha='center', va='center', fontsize=11)
        ax_iou.axis('off')
        ax_iou.set_title('Matriz IoU', fontsize=12)

    areas = [m['area'] for m in metrics]
    ax_hist_area.hist(areas, bins=15, color='coral', edgecolor='white', alpha=0.85)
    ax_hist_area.set_xlabel('Area (pixeles)')
    ax_hist_area.set_ylabel('Frecuencia')
    ax_hist_area.set_title('Distribucion de areas', fontsize=12)
    ax_hist_area.grid(alpha=0.3)

    ratios = [m['aspect_ratio'] for m in metrics if m['aspect_ratio'] is not None]
    if ratios:
        ax_hist_ratio.hist(ratios, bins=12, color='teal', edgecolor='white', alpha=0.85)
        ax_hist_ratio.set_xlabel('Relacion aspecto (W/H)')
        ax_hist_ratio.set_ylabel('Frecuencia')
        ax_hist_ratio.set_title('Distribucion de relaciones de aspecto', fontsize=12)
        ax_hist_ratio.grid(alpha=0.3)
    else:
        ax_hist_ratio.text(0.5, 0.5, 'Sin datos', ha='center', va='center')
        ax_hist_ratio.set_title('Relacion de aspecto', fontsize=12)

    centroids = [m['centroid'] for m in metrics if m['centroid'] is not None]
    if centroids:
        cxs = [c[0] for c in centroids]
        cys = [c[1] for c in centroids]
        ax_centroid.scatter(cxs, cys, c='purple', alpha=0.8, s=40, edgecolors='white', linewidths=0.5)
        ax_centroid.set_xlim(0, img_w)
        ax_centroid.set_ylim(img_h, 0)
        ax_centroid.set_aspect('equal')
        ax_centroid.set_xlabel('Coordenada X')
        ax_centroid.set_ylabel('Coordenada Y')
        ax_centroid.set_title('Centroides de mascaras', fontsize=12)
        ax_centroid.grid(alpha=0.3)
        for i, (cx, cy) in enumerate(centroids):
            ax_centroid.annotate(str(i), (cx, cy), fontsize=7, ha='center', va='bottom')
    else:
        ax_centroid.text(0.5, 0.5, 'Sin centroides validos', ha='center', va='center')
        ax_centroid.set_title('Centroides', fontsize=12)

    compactness_vals = [m['compactness'] for m in metrics]
    coverage_vals = [m['coverage_pct'] for m in metrics]
    stats_lines = [
        f"Total mascaras: {n}",
        f"Score promedio: {np.mean(scores):.3f}",
        f"",
        f"Area promedio: {np.mean(areas):.0f} px",
        f"Area minima: {min(areas):.0f} px",
        f"Area maxima: {max(areas):.0f} px",
        f"",
        f"Cobertura promedio: {np.mean(coverage_vals):.2f}%",
        f"Compacidad promedio: {np.mean(compactness_vals):.3f}",
        f"",
        f"Relacion aspecto promedio: {np.mean(ratios):.2f}" if ratios else "",
    ]
    ax_summary.text(0.05, 0.95, '\n'.join(stats_lines), fontsize=11,
                    va='top', fontfamily='monospace', transform=ax_summary.transAxes)
    ax_summary.axis('off')
    ax_summary.set_title('Resumen de metricas', fontsize=12)

    fig.suptitle(f'Analisis completo SAM - {stem}', fontsize=15, y=0.98)
    plt.savefig(str(OUTPUT_DIR / f'02_sam_auto_{stem}_composite.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> Guardado: media/python/02_sam_auto_{stem}_composite.png")


def plot_metrics_summary(masks, scores, metrics, stem):
    n = len(masks)
    colors = plt.cm.tab20(np.linspace(0, 1, max(n, 1)))[:, :3] * 255
    colors = colors.astype(np.uint8)

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))

    areas = [m['area'] for m in metrics]
    perims = [m['perimeter'] for m in metrics]
    ratios = [m['aspect_ratio'] for m in metrics if m['aspect_ratio'] is not None]
    covs = [m['coverage_pct'] for m in metrics]
    comps = [m['compactness'] for m in metrics]
    circs = [m['circularity'] for m in metrics]
    centroids = [m['centroid'] for m in metrics if m['centroid'] is not None]

    axes[0, 0].hist(areas, bins=15, color='coral', edgecolor='white', alpha=0.85)
    axes[0, 0].axvline(np.mean(areas), color='red', linestyle='--', linewidth=1.5, label=f'media={np.mean(areas):.0f}')
    axes[0, 0].set_xlabel('Area (pixeles)')
    axes[0, 0].set_ylabel('Frecuencia')
    axes[0, 0].set_title('Distribucion de areas')
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].hist(perims, bins=15, color='seagreen', edgecolor='white', alpha=0.85)
    axes[0, 1].axvline(np.mean(perims), color='darkgreen', linestyle='--', linewidth=1.5, label=f'media={np.mean(perims):.0f}')
    axes[0, 1].set_xlabel('Perimetro (pixeles)')
    axes[0, 1].set_ylabel('Frecuencia')
    axes[0, 1].set_title('Distribucion de perimetros')
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(alpha=0.3)

    if ratios:
        axes[0, 2].hist(ratios, bins=12, color='teal', edgecolor='white', alpha=0.85)
        axes[0, 2].axvline(np.mean(ratios), color='darkcyan', linestyle='--', linewidth=1.5, label=f'media={np.mean(ratios):.2f}')
        axes[0, 2].set_xlabel('Relacion de aspecto (W/H)')
        axes[0, 2].set_ylabel('Frecuencia')
        axes[0, 2].set_title('Distribucion de relacion de aspecto')
        axes[0, 2].legend(fontsize=8)
        axes[0, 2].grid(alpha=0.3)

    axes[1, 0].hist(covs, bins=12, color='orange', edgecolor='white', alpha=0.85)
    axes[1, 0].axvline(np.mean(covs), color='darkorange', linestyle='--', linewidth=1.5, label=f'media={np.mean(covs):.2f}%')
    axes[1, 0].set_xlabel('Cobertura (% de la imagen)')
    axes[1, 0].set_ylabel('Frecuencia')
    axes[1, 0].set_title('Distribucion de cobertura')
    axes[1, 0].legend(fontsize=8)
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].hist(comps, bins=12, color='mediumpurple', edgecolor='white', alpha=0.85)
    axes[1, 1].axvline(np.mean(comps), color='indigo', linestyle='--', linewidth=1.5, label=f'media={np.mean(comps):.3f}')
    axes[1, 1].set_xlabel('Compacidad (4πA/P²)')
    axes[1, 1].set_ylabel('Frecuencia')
    axes[1, 1].set_title('Distribucion de compacidad')
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].grid(alpha=0.3)

    if centroids:
        img_h, img_w = masks[0].shape[:2]
        cxs = [c[0] for c in centroids]
        cys = [c[1] for c in centroids]
        sc = axes[1, 2].scatter(cxs, cys, c=scores[:len(centroids)], cmap='plasma',
                                alpha=0.85, s=50, edgecolors='white', linewidths=0.5)
        axes[1, 2].set_xlim(0, img_w)
        axes[1, 2].set_ylim(img_h, 0)
        axes[1, 2].set_aspect('equal')
        axes[1, 2].set_xlabel('Coordenada X')
        axes[1, 2].set_ylabel('Coordenada Y')
        axes[1, 2].set_title('Centroides (color = score)')
        axes[1, 2].grid(alpha=0.3)
        plt.colorbar(sc, ax=axes[1, 2], label='Score', fraction=0.046, pad=0.04)
    else:
        axes[1, 2].text(0.5, 0.5, 'Sin centroides', ha='center', va='center')
        axes[1, 2].set_title('Centroides')

    fig.suptitle(f'Metricas de segmentacion SAM detalladas - {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'02_sam_auto_{stem}_metrics.png')


def generate_final_summary_plot(image_rgb, masks, scores, metrics, stem, img_h, img_w,
                                 discard_stats, discarded_reasons):
    n = len(masks)
    colors = plt.cm.tab20(np.linspace(0, 1, max(n, 1)))[:, :3] * 255
    colors = colors.astype(np.uint8)
    overlay = overlay_masks(image_rgb, masks, colors, alpha=0.45)

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))

    axes[0].imshow(image_rgb)
    axes[0].set_title(f'Original - {stem}', fontsize=12)
    axes[0].axis('off')

    axes[1].imshow(overlay)
    axes[1].set_title(f'Segmentacion ({n} objetos estimados)', fontsize=12)
    axes[1].axis('off')

    for i, m in enumerate(masks):
        bbox = compute_bbox(m)
        if bbox is None:
            continue
        x1, y1, x2, y2 = bbox
        c = colors[i % len(colors)] / 255.0
        rect = Rectangle((x1, y1), x2 - x1, y2 - y1,
                         linewidth=1.5, edgecolor=c, facecolor='none', linestyle='--')
        axes[1].add_patch(rect)
        cx, cy = metrics[i]['centroid']
        axes[1].plot(cx, cy, marker='x', markersize=8, color='white', mew=2)
        axes[1].text(cx + 5, cy - 5, f'{i}', fontsize=9, color='white', weight='bold')

    areas = [m['area'] for m in metrics]
    covs = [m['coverage_pct'] for m in metrics]
    comps = [m['compactness'] for m in metrics]

    summary_lines = [
        f"RESUMEN FINAL",
        f"=============",
        f"",
        f"Objetos estimados: {n}",
        f"Score promedio: {np.mean(scores):.3f}",
        f"",
        f"Areas:",
        f"  Media: {np.mean(areas):.0f} px",
        f"  Min: {min(areas):.0f} px",
        f"  Max: {max(areas):.0f} px",
        f"",
        f"Cobertura total: {sum(covs):.1f}%",
        f"Compacidad media: {np.mean(comps):.3f}",
        f"",
        f"Mascaras descartadas: {discard_stats['total_descartadas']}",
        f"  Fondo/textura: {discard_stats['fondo']}",
        f"  NMS (redundantes): {discard_stats['nms']}",
    ]

    axes[2].text(0.05, 0.95, '\n'.join(summary_lines), fontsize=11,
                 va='top', fontfamily='monospace', transform=axes[2].transAxes)
    axes[2].axis('off')
    axes[2].set_title('Resumen final', fontsize=12)

    fig.suptitle(f'Resultado final SAM - {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'02_sam_auto_{stem}_final_summary.png')


def main():
    print("=== SAM: Segmentacion Automatica Mejorada ===")
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

        masks_raw, scores_raw = generate_auto_masks(
            model, processor, image_rgb_small, device, grid_size=16
        )

        import cv2
        masks_resized = []
        for m in masks_raw:
            m_resized = cv2.resize(m.astype(np.float32),
                                    (w_img, h_img),
                                    interpolation=cv2.INTER_NEAREST)
            masks_resized.append((m_resized > 0).astype(np.uint8))
        masks_resized = np.array(masks_resized)

        masks, scores, discard_stats = filter_pipeline(masks_resized, scores_raw, h_img, w_img)

        if len(masks) == 0:
            print("  No se generaron mascaras tras filtros.")
            continue

        metrics = compute_all_metrics(masks, (h_img, w_img))

        stem = img_path.stem
        plot_comprehensive_analysis(image_rgb, masks, scores, metrics, stem, h_img, w_img)
        plot_metrics_summary(masks, scores, metrics, stem)
        generate_final_summary_plot(image_rgb, masks, scores, metrics, stem, h_img, w_img,
                                     discard_stats, None)
        print(f"  Resultados guardados para {stem}.")

    print("\n=== SAM automatico completado ===")


if __name__ == '__main__':
    main()
