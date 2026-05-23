import torch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import (
    load_image_rgb, save_and_display, overlay_masks,
    PASCAL_CLASSES, PASCAL_COLORS, compute_mask_area,
    compute_mask_perimeter, compute_iou, filter_pipeline,
    INPUT_DIR, get_device
)
from PIL import Image
import time


def segment_deeplabv3(model, preprocess, image_rgb, device):
    import cv2
    t0 = time.time()
    input_tensor = preprocess(image_rgb).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_tensor)['out']
    mask = output.argmax(1).squeeze().detach().cpu().numpy().astype(np.int32)
    h, w = image_rgb.shape[:2]
    mask = cv2.resize(mask.astype(np.float32), (w, h),
                      interpolation=cv2.INTER_NEAREST).astype(np.int32)
    elapsed = time.time() - t0
    return mask, elapsed


def segment_sam_batch(model, processor, image_rgb, device, grid_size=10):
    t0 = time.time()
    img_pil = Image.fromarray(image_rgb)
    img_pil.thumbnail((640, 640), Image.LANCZOS)
    img_small = np.array(img_pil)

    h, w = img_small.shape[:2]
    xs = np.linspace(0, w - 1, grid_size, dtype=int)
    ys = np.linspace(0, h - 1, grid_size, dtype=int)
    grid_pts = [[float(x), float(y)] for y in ys for x in xs]

    all_masks = []
    all_scores = []
    batch_size = 64
    for start in range(0, len(grid_pts), batch_size):
        batch_pts = grid_pts[start:start + batch_size]
        labels = [1] * len(batch_pts)
        inputs = processor(img_small, input_points=[batch_pts],
                           input_labels=[labels], return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
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
    elapsed = time.time() - t0
    return masks.squeeze(), scores, elapsed


def create_batch_collage(results, filename):
    n = len(results)
    if n == 0:
        return
    cols = min(4, n)
    rows = (n + cols - 1) // cols

    fig = plt.figure(figsize=(5 * cols, 5 * rows))
    gs = GridSpec(rows, cols, figure=fig)

    for idx, res in enumerate(results):
        r, c = divmod(idx, cols)
        ax = fig.add_subplot(gs[r, c])
        ax.imshow(res['sam_overlay'])
        ax.set_title(f"{res['name']}\nDL: {res['dl_classes']} cls | "
                     f"SAM: {res['sam_count']} mascaras", fontsize=9)
        ax.axis('off')

    fig.suptitle('Procesamiento por lotes: DeepLabV3 + SAM', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'05_batch_collage_{filename}.png')


def create_performance_chart(results, filename):
    names = [r['name'] for r in results]
    dl_times = [r['dl_time'] for r in results]
    sam_times = [r['sam_time'] for r in results]
    dl_classes = [r['dl_classes'] for r in results]
    sam_counts = [r['sam_count'] for r in results]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    x = np.arange(len(names))
    width = 0.35
    axes[0, 0].bar(x - width/2, dl_times, width, label='DeepLabV3', color='coral')
    axes[0, 0].bar(x + width/2, sam_times, width, label='SAM', color='steelblue')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(names, rotation=45, ha='right')
    axes[0, 0].set_ylabel('Tiempo (s)')
    axes[0, 0].set_title('Tiempo de inferencia por imagen')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].bar(x - width/2, dl_classes, width, label='DeepLabV3', color='coral')
    axes[0, 1].bar(x + width/2, sam_counts, width, label='SAM', color='steelblue')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(names, rotation=45, ha='right')
    axes[0, 1].set_ylabel('Cantidad')
    axes[0, 1].set_title('Clases vs Mascaras detectadas')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)

    axes[1, 0].scatter(dl_classes, sam_counts, c='purple', s=100, alpha=0.7)
    for i, name in enumerate(names):
        axes[1, 0].annotate(name, (dl_classes[i], sam_counts[i]),
                           fontsize=8, ha='center', va='bottom')
    axes[1, 0].set_xlabel('Clases DeepLabV3')
    axes[1, 0].set_ylabel('Mascaras SAM')
    axes[1, 0].set_title('Correlacion clases vs mascaras')
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].axis('off')
    summary = (
        f"Resumen del procesamiento por lotes\n"
        f"-----------------------------------\n"
        f"Total imagenes: {len(results)}\n"
        f"Tiempo DL promedio: {np.mean(dl_times):.2f}s\n"
        f"Tiempo SAM promedio: {np.mean(sam_times):.2f}s\n"
        f"Clases DL promedio: {np.mean(dl_classes):.1f}\n"
        f"Mascaras SAM promedio: {np.mean(sam_counts):.1f}"
    )
    axes[1, 1].text(0.1, 0.5, summary, fontsize=12, va='center',
                    fontfamily='monospace')

    fig.suptitle('Rendimiento: DeepLabV3 vs SAM', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'05_batch_performance_{filename}.png')


def create_detailed_results(results, filename):
    for res in results:
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        axes[0].imshow(res['original'])
        axes[0].set_title(f"Original: {res['name']}")
        axes[0].axis('off')

        axes[1].imshow(res['dl_overlay'])
        detected = [PASCAL_CLASSES[c] for c in np.unique(res['dl_mask'])
                    if 0 < c < len(PASCAL_CLASSES)]
        axes[1].set_title(f"DeepLabV3: {', '.join(detected[:5])}")
        axes[1].axis('off')

        axes[2].imshow(res['sam_overlay'])
        axes[2].set_title(f"SAM: {res['sam_count']} mascaras")
        axes[2].axis('off')

        fig.suptitle(f'Resultados detallados - {res["name"]}', fontsize=14)
        plt.tight_layout()
        save_and_display(fig, f'05_detailed_{res["name"]}.png')


def main():
    print("=== Procesamiento por Lotes: DeepLabV3 + SAM ===")
    device = get_device()
    print(f"Dispositivo: {device}")

    import torchvision.transforms as T
    from torchvision import models
    from transformers import SamModel, SamProcessor

    print("Cargando modelos...")
    dl_model = models.segmentation.deeplabv3_resnet101(pretrained=True).to(device)
    dl_model.eval()
    preprocess = T.Compose([
        T.ToPILImage(), T.Resize(520), T.ToTensor(),
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

    results = []
    for i, img_path in enumerate(image_files[:5]):
        print(f"\n[{i+1}/{len(image_files)}] Procesando: {img_path.name}")
        image_rgb = load_image_rgb(img_path)

        dl_mask, dl_time = segment_deeplabv3(dl_model, preprocess, image_rgb, device)
        masks, scores, sam_time = segment_sam_batch(
            sam_model, processor, image_rgb, device, grid_size=10
        )

        import cv2
        h_orig, w_orig = image_rgb.shape[:2]
        masks_bin_list = []
        for m in masks:
            m_resized = cv2.resize(m.astype(np.float32), (w_orig, h_orig),
                                   interpolation=cv2.INTER_NEAREST)
            masks_bin_list.append((m_resized > 0).astype(np.uint8))
        masks_bin = np.array(masks_bin_list)
        masks_bin, scores, _ = filter_pipeline(masks_bin, scores, h_orig, w_orig)

        dl_classes = len([c for c in np.unique(dl_mask)
                         if 0 < c < len(PASCAL_CLASSES)])

        dl_overlay = image_rgb.copy().astype(np.float32)
        for cls in np.unique(dl_mask):
            if 0 < cls < len(PASCAL_CLASSES):
                color = PASCAL_COLORS[cls].astype(np.float32)
                mask_dl = dl_mask == cls
                for c in range(3):
                    dl_overlay[:, :, c] = np.where(
                        mask_dl,
                        dl_overlay[:, :, c] * 0.5 + color[c] * 0.5,
                        dl_overlay[:, :, c]
                    )

        colors = np.random.randint(0, 255, (max(len(masks_bin), 1), 3), dtype=np.uint8)
        sam_overlay = overlay_masks(image_rgb, masks_bin[:50], colors, alpha=0.4)

        results.append({
            'name': img_path.stem,
            'original': image_rgb,
            'dl_mask': dl_mask,
            'dl_overlay': dl_overlay.astype(np.uint8),
            'sam_overlay': sam_overlay,
            'dl_classes': dl_classes,
            'sam_count': len(masks_bin),
            'dl_time': dl_time,
            'sam_time': sam_time,
        })

        print(f"  DL: {dl_classes} clases ({dl_time:.2f}s), "
              f"SAM: {len(masks_bin)} mascaras ({sam_time:.2f}s)")

    print(f"\n=== Generando visualizaciones resumen ===")
    create_batch_collage(results, 'overview')
    create_performance_chart(results, 'overview')
    create_detailed_results(results, 'overview')
    print("\n=== Procesamiento por lotes completado ===")


if __name__ == '__main__':
    main()
