import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import torch

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / 'media'
INPUT_DIR = MEDIA_DIR / 'input'
OUTPUT_DIR = MEDIA_DIR / 'python'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PASCAL_COLORS = np.array([
    [0, 0, 0], [128, 0, 0], [0, 128, 0], [128, 128, 0],
    [0, 0, 128], [128, 0, 128], [0, 128, 128], [128, 128, 128],
    [64, 0, 0], [192, 0, 0], [64, 128, 0], [192, 128, 0],
    [64, 0, 128], [192, 0, 128], [64, 128, 128], [192, 128, 128],
    [0, 64, 0], [128, 64, 0], [0, 192, 0], [128, 192, 0],
    [0, 64, 128]
], dtype=np.uint8)

PASCAL_CLASSES = [
    'fondo', 'avion', 'bicicleta', 'pajaro', 'barco',
    'botella', 'autobus', 'coche', 'gato', 'silla',
    'vaca', 'mesa', 'perro', 'caballo', 'moto',
    'persona', 'planta', 'oveja', 'sofa', 'tren',
    'tv'
]


def ensure_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_image_rgb(path):
    path = str(path)
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"No se encontro la imagen: {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def load_image(path, flags=cv2.IMREAD_COLOR):
    path = str(path)
    img = cv2.imread(path, flags)
    if img is None:
        raise FileNotFoundError(f"No se encontro la imagen: {path}")
    return img


def save_and_display(fig, filename, dpi=150):
    filepath = OUTPUT_DIR / filename
    fig.savefig(str(filepath), dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f"  -> Guardado: {filepath.relative_to(BASE_DIR)}")
    return filepath


def overlay_masks(image, masks, colors=None, alpha=0.5):
    overlay = image.copy().astype(np.float32)
    if colors is None:
        colors = np.random.randint(0, 255, (len(masks), 3), dtype=np.uint8)
    colors = np.asarray(colors, dtype=np.float32)
    if colors.ndim == 3:
        colors = colors.reshape(-1, 3)
    for i, mask in enumerate(masks):
        if mask.ndim == 3:
            mask = mask.squeeze()
        idx = i % len(colors)
        for c in range(3):
            overlay[:, :, c] = np.where(
                mask > 0,
                overlay[:, :, c] * (1 - alpha) + colors[idx, c] * alpha,
                overlay[:, :, c]
            )
    return overlay.astype(np.uint8)


def get_device():
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')


def compute_mask_area(mask):
    return int(np.sum(mask > 0))


def compute_mask_perimeter(mask):
    binary = (mask > 0).astype(np.uint8) * 255
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    perimeter = 0
    for cnt in contours:
        perimeter += cv2.arcLength(cnt, True)
    return perimeter


def compute_mask_centroid(mask):
    binary = (mask > 0).astype(np.uint8)
    moments = cv2.moments(binary)
    if moments['m00'] == 0:
        return None
    cx = int(moments['m10'] / moments['m00'])
    cy = int(moments['m01'] / moments['m00'])
    return (cx, cy)


def compute_iou(mask1, mask2):
    intersection = np.logical_and(mask1 > 0, mask2 > 0).sum()
    union = np.logical_or(mask1 > 0, mask2 > 0).sum()
    if union == 0:
        return 0.0
    return intersection / union
