import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import time

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / 'media'
OUTPUT_DIR = BASE_DIR / 'python' / 'output'

IMAGES = {
    'box': str(MEDIA_DIR / 'box.png'),
    'box_in_scene': str(MEDIA_DIR / 'box_in_scene.png'),
    'bike': str(MEDIA_DIR / 'bike.jpg'),
}


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def load_image(path, flags=cv2.IMREAD_GRAYSCALE):
    img = cv2.imread(path, flags)
    if img is None:
        raise FileNotFoundError(f'Could not load image: {path}')
    return img


def load_image_rgb(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f'Could not load image: {path}')
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def detect_and_compute(img, method='sift'):
    if method == 'sift':
        detector = cv2.SIFT_create()
    elif method == 'orb':
        detector = cv2.ORB_create()
    else:
        raise ValueError(f'Unknown method: {method}')
    kp, des = detector.detectAndCompute(img, None)
    return kp, des, detector


def draw_matches(img1, kp1, img2, kp2, matches, max_draw=100):
    sorted_matches = sorted(matches, key=lambda x: x.distance)
    draw_matches = sorted_matches[:max_draw]
    return cv2.drawMatches(
        img1, kp1, img2, kp2, draw_matches, None,
        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
    )


def filter_good_matches_ratio(matches, ratio=0.75):
    good = []
    for match_pair in matches:
        if len(match_pair) < 2:
            continue
        m, n = match_pair
        if m.distance < ratio * n.distance:
            good.append(m)
    return good


def timer_func(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed
    return wrapper


def save_and_display(fig, filename, dpi=150):
    output_dir = ensure_output_dir()
    path = output_dir / filename
    fig.savefig(str(path), dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {path}')
    return path
