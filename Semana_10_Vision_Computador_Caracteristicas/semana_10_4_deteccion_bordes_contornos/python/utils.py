import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import time


BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / 'media'
PYTHON_MEDIA_DIR = MEDIA_DIR / 'python'

IMAGES = {
    'bike': str(MEDIA_DIR / 'bike.jpg'),
}


def ensure_python_media_dir():
    PYTHON_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    return PYTHON_MEDIA_DIR


def load_image(path, flags=cv2.IMREAD_GRAYSCALE):
    img = cv2.imread(path, flags)
    if img is None:
        raise FileNotFoundError(f'No se pudo cargar la imagen: {path}')
    return img


def load_image_rgb(path):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f'No se pudo cargar la imagen: {path}')
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def timer_func(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed
    return wrapper


def save_and_display(fig, filename, dpi=150):
    output_dir = ensure_python_media_dir()
    path = output_dir / filename
    fig.savefig(str(path), dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    print(f'Guardado: {path}')
    return path


def create_test_image_shapes():
    img = np.ones((500, 700, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (50, 50), (200, 200), (100, 100, 100), -1)
    cv2.circle(img, (400, 125), 75, (100, 100, 100), -1)
    cv2.rectangle(img, (550, 50), (650, 200), (100, 100, 100), -1)
    pts = np.array([[50, 400], [125, 300], [200, 400]], dtype=np.int32)
    cv2.fillPoly(img, [pts], (100, 100, 100))
    cv2.rectangle(img, (300, 300), (500, 450), (100, 100, 100), -1)
    pts2 = np.array([[580, 300], [680, 300], [680, 400], [580, 430]], dtype=np.int32)
    cv2.fillPoly(img, [pts2], (100, 100, 100))
    return img


def create_test_image_defects():
    img = np.ones((400, 600, 3), dtype=np.uint8) * 240
    cv2.circle(img, (150, 200), 80, (80, 80, 80), -1)
    cv2.circle(img, (150, 200), 15, (0, 0, 0), -1)
    cv2.rectangle(img, (350, 100), (500, 300), (80, 80, 80), -1)
    cv2.rectangle(img, (410, 180), (440, 220), (0, 0, 0), -1)
    cv2.circle(img, (100, 80), 50, (80, 80, 80), -1)
    return img
