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


def compute_bbox(mask):
    binary = (mask > 0).astype(np.uint8)
    ys, xs = np.where(binary)
    if len(xs) == 0 or len(ys) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def compute_bbox_aspect_ratio(mask):
    bbox = compute_bbox(mask)
    if bbox is None:
        return None
    x1, y1, x2, y2 = bbox
    w = x2 - x1 + 1
    h = y2 - y1 + 1
    if h == 0:
        return None
    return w / h


def compute_coverage_pct(mask):
    h, w = mask.shape[:2]
    total_px = h * w
    if total_px == 0:
        return 0.0
    return (compute_mask_area(mask) / total_px) * 100.0


def compute_compactness(mask):
    area = compute_mask_area(mask)
    perim = compute_mask_perimeter(mask)
    if perim == 0 or area == 0:
        return 0.0
    return (4 * np.pi * area) / (perim * perim)


def compute_circularity(mask):
    return compute_compactness(mask)


def filter_masks_by_ratio(mask, min_ratio=0.2, max_ratio=5.0):
    ratio = compute_bbox_aspect_ratio(mask)
    if ratio is None:
        return False
    return min_ratio <= ratio <= max_ratio


def filter_masks_by_coverage(mask, max_pct=50.0, min_pct=0.05):
    cov = compute_coverage_pct(mask)
    return min_pct <= cov <= max_pct


def filter_masks_by_area(mask, min_area=400, image_area=None):
    area = compute_mask_area(mask)
    if area < min_area:
        return False
    if image_area is not None and area > image_area * 0.85:
        return False
    return True


def enhanced_nms(masks, scores, iou_threshold=0.5, score_threshold=0.85):
    flat_scores = scores.flatten()
    sorted_idxs = np.argsort(flat_scores)[::-1]
    keep = []
    kept_indices = set()
    for idx in sorted_idxs:
        if flat_scores[idx] < score_threshold:
            continue
        redundant = False
        for k in keep:
            if compute_iou(masks[idx], masks[k]) > iou_threshold:
                redundant = True
                break
        if not redundant:
            keep.append(idx)
            kept_indices.add(idx)
    return keep


def filter_background_masks(masks, scores, img_h, img_w, discarded_reasons=None,
                             max_coverage=40.0, min_coverage=0.05,
                             min_ratio=0.2, max_ratio=5.0,
                             min_compactness=0.01,
                             min_area=400):
    image_area = img_h * img_w
    keep = []
    for i in range(len(masks)):
        reasons = []
        if not filter_masks_by_area(masks[i], min_area=min_area, image_area=image_area):
            reasons.append('area_fuera_rango')
        if not filter_masks_by_coverage(masks[i], max_pct=max_coverage, min_pct=min_coverage):
            cov = compute_coverage_pct(masks[i])
            reasons.append(f'cobertura_{cov:.1f}%')
        if not filter_masks_by_ratio(masks[i], min_ratio=min_ratio, max_ratio=max_ratio):
            ratio = compute_bbox_aspect_ratio(masks[i])
            reasons.append(f'aspecto_{ratio:.2f}')
        comp = compute_compactness(masks[i])
        if comp < min_compactness:
            reasons.append(f'baja_compacidad_{comp:.4f}')
        if reasons:
            if discarded_reasons is not None:
                discarded_reasons[i] = reasons
        else:
            keep.append(i)
    return keep


def filter_pipeline(masks, scores, img_h, img_w,
                    max_coverage=40.0, min_coverage=0.05,
                    min_ratio=0.2, max_ratio=5.0,
                    min_compactness=0.01, min_area=400,
                    nms_iou=0.5, nms_score=0.85):
    n_before = len(masks)

    bg_keep = filter_background_masks(
        masks, scores, img_h, img_w,
        max_coverage=max_coverage, min_coverage=min_coverage,
        min_ratio=min_ratio, max_ratio=max_ratio,
        min_compactness=min_compactness, min_area=min_area
    )

    masks = masks[bg_keep]
    scores = scores[bg_keep]
    n_after_bg = len(masks)

    keep = enhanced_nms(masks, scores, iou_threshold=nms_iou, score_threshold=nms_score)
    masks = masks[keep]
    scores = scores[keep]

    print(f"    Filtro: {n_before} -> fondo/textura: {n_before - n_after_bg} "
          f"| NMS: {n_after_bg - len(masks)} "
          f"| final: {len(masks)}")
    return masks, scores, {
        'fondo': n_before - n_after_bg,
        'nms': n_after_bg - len(masks),
        'total_descartadas': n_before - len(masks)
    }
