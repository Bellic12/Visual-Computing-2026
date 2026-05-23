import torch
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import (
    load_image_rgb, save_and_display, PASCAL_CLASSES, PASCAL_COLORS,
    compute_mask_area, compute_mask_perimeter, compute_mask_centroid,
    compute_iou, filter_pipeline, INPUT_DIR, get_device
)
from PIL import Image


def deeplabv3_segment(model, preprocess, image_rgb, device):
    input_tensor = preprocess(image_rgb).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_tensor)['out']
    mask = output.argmax(1).squeeze().detach().cpu().numpy().astype(np.int32)
    import cv2
    h, w = image_rgb.shape[:2]
    mask = cv2.resize(mask.astype(np.float32), (w, h),
                      interpolation=cv2.INTER_NEAREST).astype(np.int32)
    return mask


def get_class_masks(mask_idx):
    classes = np.unique(mask_idx)
    masks = {}
    for c in classes:
        if 0 < c < len(PASCAL_CLASSES):
            masks[c] = (mask_idx == c).astype(np.uint8)
    return masks


def process_single_image(image_rgb, deeplab_mask, sam_masks, sam_scores, stem):
    dl_masks = get_class_masks(deeplab_mask)
    detected = sorted(dl_masks.keys())
    n_detected = len(detected)
    n_sam = len(sam_masks)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    colors = np.random.randint(0, 255, (max(n_sam, 1), 3), dtype=np.uint8)

    dl_overlay = image_rgb.copy().astype(np.float32)
    for cls in detected:
        color = PASCAL_COLORS[cls].tolist()
        mask = dl_masks[cls] > 0
        for c in range(3):
            dl_overlay[:, :, c] = np.where(
                mask, dl_overlay[:, :, c] * 0.5 + color[c] * 0.5,
                dl_overlay[:, :, c]
            )
    axes[0].imshow(dl_overlay.astype(np.uint8))
    axes[0].set_title(f'DeepLabV3 - {n_detected} clases')
    axes[0].axis('off')

    if n_sam > 0:
        sam_overlay = image_rgb.copy().astype(np.float32)
        for i, mask in enumerate(sam_masks[:50]):
            color = colors[i % len(colors)].astype(np.float32)
            for c in range(3):
                sam_overlay[:, :, c] = np.where(
                    mask > 0, sam_overlay[:, :, c] * 0.6 + color[c] * 0.4,
                    sam_overlay[:, :, c]
                )
        axes[1].imshow(sam_overlay.astype(np.uint8))
        axes[1].set_title(f'SAM - {n_sam} mascaras')
    else:
        axes[1].imshow(image_rgb)
        axes[1].set_title('SAM - sin mascaras tras filtro')
    axes[1].axis('off')

    fig.suptitle(f'Comparacion: DeepLabV3 vs SAM - {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'04_comparison_{stem}.png')


def compute_metrics_table(dl_masks, sam_masks, stem):
    rows = []
    for cls, mask in dl_masks.items():
        area = compute_mask_area(mask)
        perim = compute_mask_perimeter(mask)
        cent = compute_mask_centroid(mask)
        rows.append({
            'tipo': 'DeepLabV3',
            'clase': PASCAL_CLASSES[cls],
            'area': area,
            'perimetro': perim,
            'centroide': cent
        })

    for i, mask in enumerate(sam_masks[:20]):
        area = compute_mask_area(mask)
        perim = compute_mask_perimeter(mask)
        cent = compute_mask_centroid(mask)
        rows.append({
            'tipo': 'SAM',
            'clase': f'mascara_{i}',
            'area': area,
            'perimetro': perim,
            'centroide': cent
        })

    if len(rows) == 0:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.text(0.5, 0.5, 'Sin datos de segmentacion para esta imagen',
                ha='center', va='center', fontsize=12)
        ax.axis('off')
        fig.suptitle(f'Metricas de segmentacion - {stem}', fontsize=14)
        plt.tight_layout()
        save_and_display(fig, f'04_metrics_table_{stem}.png')
        return

    fig, ax = plt.subplots(figsize=(14, max(4, len(rows) * 0.4)))
    ax.axis('off')

    col_labels = ['Tipo', 'Clase / Mascara', 'Area (px)', 'Perimetro (px)',
                  'Centroide']
    cell_data = []
    for r in rows:
        cent_str = f"({r['centroide'][0]}, {r['centroide'][1]})" if r['centroide'] else 'N/A'
        cell_data.append([r['tipo'], r['clase'], str(r['area']),
                          f"{r['perimetro']:.1f}", cent_str])

    table = ax.table(
        cellText=cell_data,
        colLabels=col_labels,
        cellLoc='center',
        loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)

    fig.suptitle(f'Metricas de segmentacion - {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'04_metrics_table_{stem}.png')


def compute_cross_iou(dl_masks, sam_masks, stem):
    detected = sorted(dl_masks.keys())
    if len(detected) == 0 or len(sam_masks) == 0:
        print("  No hay suficientes mascaras para IoU cruzado.")
        return

    n_sam = min(len(sam_masks), 30)
    iou_matrix = np.zeros((len(detected), n_sam))
    for i, cls in enumerate(detected):
        for j in range(n_sam):
            iou_matrix[i, j] = compute_iou(
                dl_masks[cls], sam_masks[j]
            )

    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(iou_matrix, cmap='viridis', aspect='auto', vmin=0, vmax=1)
    ax.set_xticks(range(n_sam))
    ax.set_xticklabels([f'SAM{j}' for j in range(n_sam)], rotation=45, ha='right')
    ax.set_yticks(range(len(detected)))
    ax.set_yticklabels([PASCAL_CLASSES[c] for c in detected])
    ax.set_xlabel('Mascaras SAM')
    ax.set_ylabel('Clases DeepLabV3')

    for i in range(len(detected)):
        for j in range(n_sam):
            val = iou_matrix[i, j]
            color = 'white' if val > 0.5 else 'black'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                    fontsize=7, color=color)

    plt.colorbar(im, ax=ax, label='IoU')
    fig.suptitle(f'Matriz IoU: DeepLabV3 vs SAM - {stem}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'04_iou_heatmap_{stem}.png')

    best_iou = iou_matrix.max(axis=1)
    print(f"  Mejor IoU por clase DeepLabV3 vs SAM:")
    for i, cls in enumerate(detected):
        print(f"    {PASCAL_CLASSES[cls]}: {best_iou[i]:.3f}")


def main():
    print("=== Analisis de Metricas de Segmentacion ===")
    device = get_device()
    print(f"Dispositivo: {device}")

    import torchvision.transforms as T
    from torchvision import models
    from transformers import SamModel, SamProcessor

    print("Cargando modelos...")
    dl_model = models.segmentation.deeplabv3_resnet101(pretrained=True).to(device)
    dl_model.eval()

    preprocess = T.Compose([
        T.ToPILImage(),
        T.Resize(520),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    sam_model = SamModel.from_pretrained("facebook/sam-vit-base").to(device)
    processor = SamProcessor.from_pretrained("facebook/sam-vit-base")
    sam_model.eval()
    print("Modelos cargados.")

    image_files = sorted(INPUT_DIR.glob('*.jpg')) + sorted(INPUT_DIR.glob('*.png'))
    if not image_files:
        print("No se encontraron imagenes. Ejecuta download_images.py primero.")
        return

    for i, img_path in enumerate(image_files[:3]):
        print(f"\n[{i+1}/{len(image_files)}] Procesando: {img_path.name}")
        image_rgb = load_image_rgb(img_path)

        print("  Ejecutando DeepLabV3...")
        dl_mask = deeplabv3_segment(dl_model, preprocess, image_rgb, device)

        print("  Ejecutando SAM...")
        img_pil = Image.fromarray(image_rgb)
        h_small = img_pil.size[1]
        img_pil.thumbnail((640, 640), Image.LANCZOS)
        image_small = np.array(img_pil)

        xs = np.linspace(0, image_small.shape[1] - 1, 10, dtype=int)
        ys = np.linspace(0, image_small.shape[0] - 1, 10, dtype=int)
        grid_pts = [[float(x), float(y)] for y in ys for x in xs]
        all_masks = []
        all_scores = []
        batch_size = 64
        for start in range(0, len(grid_pts), batch_size):
            batch_pts = grid_pts[start:start + batch_size]
            labels = [1] * len(batch_pts)
            inputs = processor(image_small, input_points=[batch_pts],
                               input_labels=[labels], return_tensors="pt").to(device)
            with torch.no_grad():
                outputs = sam_model(**inputs)
            masks = processor.image_processor.post_process_masks(
                outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(),
                inputs["reshaped_input_sizes"].cpu()
            )[0].numpy()
            scores = outputs.iou_scores.cpu().numpy()[0]
            all_masks.append(masks)
            all_scores.append(scores)
        masks = np.concatenate(all_masks, axis=0)
        scores = np.concatenate(all_scores, axis=0)
        B, C, H, W = masks.shape
        masks = masks.reshape(B * C, H, W)
        scores = scores.flatten()
        import cv2
        h_orig, w_orig = image_rgb.shape[:2]
        masks_resized_list = []
        for m in masks:
            m_resized = cv2.resize(m.astype(np.float32), (w_orig, h_orig),
                                   interpolation=cv2.INTER_NEAREST)
            masks_resized_list.append((m_resized > 0).astype(np.uint8))
        masks_bin = np.array(masks_resized_list)
        masks_bin, scores, _, _ = filter_pipeline(masks_bin, scores, h_orig, w_orig)

        stem = img_path.stem
        print(f"  DeepLabV3: {len(np.unique(dl_mask))-1} clases, "
              f"SAM: {len(masks_bin)} mascaras")
        process_single_image(image_rgb, dl_mask, masks_bin, scores, stem)
        compute_metrics_table(
            {c: (dl_mask == c).astype(np.uint8) for c in np.unique(dl_mask) if 0 < c < len(PASCAL_CLASSES)},
            masks_bin, stem
        )
        compute_cross_iou(
            {c: (dl_mask == c).astype(np.uint8) for c in np.unique(dl_mask) if 0 < c < len(PASCAL_CLASSES)},
            masks_bin, stem
        )

    print("\n=== Analisis de metricas completado ===")


if __name__ == '__main__':
    main()
