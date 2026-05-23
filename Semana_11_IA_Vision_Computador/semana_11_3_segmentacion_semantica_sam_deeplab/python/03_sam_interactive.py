import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import (
    load_image_rgb, save_and_display, overlay_masks,
    INPUT_DIR, get_device
)
from PIL import Image


def segment_with_points(model, processor, image_rgb, points, labels, device):
    pts_list = [[float(p[0]), float(p[1])] for p in points]
    lbl_list = [int(l) for l in labels]
    inputs = processor(
        image_rgb,
        input_points=[pts_list],
        input_labels=[lbl_list],
        return_tensors="pt"
    ).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    masks = processor.image_processor.post_process_masks(
        outputs.pred_masks.cpu(),
        inputs["original_sizes"].cpu(),
        inputs["reshaped_input_sizes"].cpu()
    )[0].numpy()
    scores = outputs.iou_scores.cpu().numpy()[0]
    B, C, H, W = masks.shape
    masks = masks.reshape(B * C, H, W)
    scores = scores.flatten()
    return masks, scores


def segment_with_bbox(model, processor, image_rgb, bbox, device):
    bbox_float = [float(b) for b in bbox]
    inputs = processor(
        image_rgb,
        input_boxes=[[bbox_float]],
        return_tensors="pt"
    ).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    masks = processor.image_processor.post_process_masks(
        outputs.pred_masks.cpu(),
        inputs["original_sizes"].cpu(),
        inputs["reshaped_input_sizes"].cpu()
    )[0].numpy()
    scores = outputs.iou_scores.cpu().numpy()[0]
    B, C, H, W = masks.shape
    masks = masks.reshape(B * C, H, W)
    scores = scores.flatten()
    return masks, scores


def plot_point_prompt(image_rgb, masks, scores, points, stem):
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    axes[0].imshow(image_rgb)
    pts_arr = np.array(points)
    axes[0].scatter(pts_arr[:, 0], pts_arr[:, 1],
                    c='red', s=100, marker='x', linewidths=3)
    axes[0].set_title('Punto de referencia')
    axes[0].axis('off')

    titles = ['Mascara 1 (mejor)', 'Mascara 2', 'Mascara 3']
    for i in range(min(3, len(masks))):
        overlay = overlay_masks(
            image_rgb, [masks[i].squeeze() > 0],
            [np.array([[255, 0, 0]])], alpha=0.4
        )
        axes[i + 1].imshow(overlay)
        axes[i + 1].set_title(f'{titles[i]}\nscore={scores[i]:.3f}')
        axes[i + 1].axis('off')

    fig.suptitle(f'SAM - Segmentacion por punto - {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'03_sam_point_{stem}.png')


def plot_bbox_prompt(image_rgb, masks, scores, bbox, stem):
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    img_with_bbox = image_rgb.copy()
    from matplotlib.patches import Rectangle
    axes[0].imshow(img_with_bbox)
    rect = Rectangle(
        (bbox[0], bbox[1]), bbox[2] - bbox[0], bbox[3] - bbox[1],
        linewidth=2, edgecolor='lime', facecolor='none'
    )
    axes[0].add_patch(rect)
    axes[0].set_title('Caja delimitadora')
    axes[0].axis('off')

    titles = ['Mascara 1 (mejor)', 'Mascara 2', 'Mascara 3']
    for i in range(min(3, len(masks))):
        overlay = overlay_masks(
            image_rgb, [masks[i].squeeze() > 0],
            [np.array([[0, 255, 0]])], alpha=0.4
        )
        axes[i + 1].imshow(overlay)
        axes[i + 1].set_title(f'{titles[i]}\nscore={scores[i]:.3f}')
        axes[i + 1].axis('off')

    fig.suptitle(f'SAM - Segmentacion por caja - {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'03_sam_bbox_{stem}.png')


def plot_point_vs_bbox_comparison(image_rgb, point_masks, point_scores,
                                   bbox_masks, bbox_scores, stem):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    point_overlay = overlay_masks(
        image_rgb, [point_masks[0].squeeze() > 0],
        [np.array([[255, 0, 0]])], alpha=0.4
    )
    axes[0].imshow(point_overlay)
    axes[0].set_title(f'Punto (score={point_scores[0]:.3f})')
    axes[0].axis('off')

    bbox_overlay = overlay_masks(
        image_rgb, [bbox_masks[0].squeeze() > 0],
        [np.array([[0, 255, 0]])], alpha=0.4
    )
    axes[1].imshow(bbox_overlay)
    axes[1].set_title(f'Caja (score={bbox_scores[0]:.3f})')
    axes[1].axis('off')

    scores_data = [point_scores.tolist(), bbox_scores.tolist()]
    labels_data = ['Punto', 'Caja']
    bp = axes[2].boxplot(scores_data, tick_labels=labels_data, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightcoral')
    bp['boxes'][1].set_facecolor('lightgreen')
    axes[2].set_ylabel('IoU prediction score')
    axes[2].set_title('Comparacion de scores')
    axes[2].grid(alpha=0.3)

    fig.suptitle(f'SAM - Punto vs Caja - {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'03_sam_comparison_{stem}.png')


def get_center_point(mask):
    ys, xs = np.where(mask.squeeze() > 0)
    if len(xs) == 0 or len(ys) == 0:
        return None
    return np.array([[int(np.mean(xs)), int(np.mean(ys))]])


def get_bounding_box(mask):
    ys, xs = np.where(mask.squeeze() > 0)
    if len(xs) == 0 or len(ys) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]


def process_image_with_sam(model, processor, image_rgb, device, img_stem):
    h, w = image_rgb.shape[:2]

    point_prompts = [
        ('centro', [[float(w // 2), float(h // 2)]], [1]),
    ]

    print(f"  Segmentando por punto...", end=' ')
    for label, pt, lbl in point_prompts:
        masks, scores = segment_with_points(model, processor, image_rgb,
                                                     pt, lbl, device)
        plot_point_prompt(image_rgb, masks, scores, pt, img_stem)
    print('OK')

    best_mask = masks[0].squeeze() > 0
    bbox = get_bounding_box(best_mask)
    if bbox is not None:
        print(f"  Segmentando por caja {bbox}...", end=' ')
        masks_b, scores_b = segment_with_bbox(model, processor,
                                                        image_rgb, bbox, device)
        plot_bbox_prompt(image_rgb, masks_b, scores_b, bbox, img_stem)
        plot_point_vs_bbox_comparison(
            image_rgb, masks, scores, masks_b, scores_b, img_stem
        )
        print('OK')
    else:
        print("  No se pudo calcular caja.")


def main():
    print("=== SAM: Segmentacion Interactiva ===")
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

    for i, img_path in enumerate(image_files[:2]):
        print(f"\n[{i+1}/{len(image_files)}] Procesando: {img_path.name}")
        image_rgb = load_image_rgb(img_path)
        img_pil = Image.fromarray(image_rgb)
        img_pil.thumbnail((480, 480), Image.LANCZOS)
        image_small = np.array(img_pil)

        process_image_with_sam(model, processor, image_small, device, img_path.stem)
        print(f"  Resultados guardados para {img_path.stem}.")

    print("\n=== SAM interactivo completado ===")


if __name__ == '__main__':
    main()
