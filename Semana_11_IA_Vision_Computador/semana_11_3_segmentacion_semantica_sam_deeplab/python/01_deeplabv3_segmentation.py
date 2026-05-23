import torch
import torchvision.transforms as T
from torchvision import models
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import (
    load_image_rgb, save_and_display, PASCAL_COLORS,
    PASCAL_CLASSES, INPUT_DIR, get_device
)


def get_pascal_palette():
    palette = np.zeros((256, 3), dtype=np.uint8)
    palette[:len(PASCAL_COLORS)] = PASCAL_COLORS
    return palette


def colorize_mask(mask_idx, palette):
    h, w = mask_idx.shape
    color_mask = np.zeros((h, w, 3), dtype=np.uint8)
    for cls in range(1, len(PASCAL_CLASSES)):
        color_mask[mask_idx == cls] = palette[cls]
    return color_mask


def segment_deeplabv3(model, image_rgb, device):
    preprocess = T.Compose([
        T.ToPILImage(),
        T.Resize(520),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(image_rgb).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_tensor)['out']
    output_predictions = output.argmax(1).squeeze().detach().cpu().numpy()
    h_orig, w_orig = image_rgb.shape[:2]
    import cv2
    mask_resized = cv2.resize(output_predictions.astype(np.float32),
                              (w_orig, h_orig), interpolation=cv2.INTER_NEAREST)
    mask_resized = mask_resized.astype(np.int32)
    return mask_resized


def get_detected_classes(mask_idx):
    classes = np.unique(mask_idx)
    return [c for c in classes if 0 < c < len(PASCAL_CLASSES)]


def binary_masks_per_class(mask_idx, classes):
    masks = {}
    for c in classes:
        masks[c] = (mask_idx == c).astype(np.uint8)
    return masks


def plot_results(image_rgb, mask_idx, filename_base):
    h, w = image_rgb.shape[:2]
    detected = get_detected_classes(mask_idx)
    palette = get_pascal_palette()
    colored_mask = colorize_mask(mask_idx, palette)
    blended = (image_rgb * 0.5 + colored_mask * 0.5).astype(np.uint8)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes[0].imshow(image_rgb)
    axes[0].set_title('Imagen original')
    axes[0].axis('off')

    axes[1].imshow(colored_mask)
    axes[1].set_title('Mascara segmentacion (PASCAL VOC)')
    axes[1].axis('off')

    axes[2].imshow(blended)
    axes[2].set_title('Superposicion (alpha=0.5)')
    axes[2].axis('off')

    fig.suptitle(f'DeepLabV3 - Clases detectadas: {len(detected)}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig, f'01_deeplabv3_{filename_base}_overview.png')

    n_classes = len(detected)
    if n_classes == 0:
        return

    n_total = n_classes + 1
    cols = min(4, n_total)
    rows = (n_total + cols - 1) // cols
    fig2, axes2 = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes2 = axes2.flatten() if rows * cols > 1 else [axes2]

    axes2[0].imshow(image_rgb)
    axes2[0].set_title('Original', fontsize=10, fontweight='bold')
    axes2[0].axis('off')

    for idx, cls in enumerate(detected):
        pos = idx + 1
        binary = (mask_idx == cls).astype(np.uint8) * 255
        axes2[pos].imshow(binary, cmap='gray')
        axes2[pos].set_title(f'{PASCAL_CLASSES[cls]} (ID {cls})')
        axes2[pos].axis('off')

    for idx in range(n_total, len(axes2)):
        axes2[idx].axis('off')

    fig2.suptitle(f'Mascaras binarias por clase - {filename_base}', fontsize=14)
    plt.tight_layout()
    save_and_display(fig2, f'01_deeplabv3_{filename_base}_masks.png')


def main():
    print("=== DeepLabV3: Segmentacion Semantica ===")
    device = get_device()
    print(f"Dispositivo: {device}")

    print("Cargando modelo DeepLabV3-ResNet101...")
    model = models.segmentation.deeplabv3_resnet101(pretrained=True).to(device)
    model.eval()
    print("Modelo cargado.")

    image_files = sorted(INPUT_DIR.glob('*.jpg')) + sorted(INPUT_DIR.glob('*.png'))
    if not image_files:
        print("No se encontraron imagenes. Ejecuta download_images.py primero.")
        return

    for i, img_path in enumerate(image_files):
        print(f"\n[{i+1}/{len(image_files)}] Procesando: {img_path.name}")
        image_rgb = load_image_rgb(img_path)
        mask_idx = segment_deeplabv3(model, image_rgb, device)
        detected = get_detected_classes(mask_idx)
        print(f"  Clases detectadas: {[PASCAL_CLASSES[c] for c in detected]}")
        stem = img_path.stem
        plot_results(image_rgb, mask_idx, stem)
        print(f"  Resultados guardados.")

    print("\n=== Procesamiento DeepLabV3 completado ===")


if __name__ == '__main__':
    main()
