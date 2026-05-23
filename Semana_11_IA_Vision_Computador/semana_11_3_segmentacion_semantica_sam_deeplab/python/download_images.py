import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import INPUT_DIR, MEDIA_DIR

COCO_IMAGES = {
    'person_dog': '000000000139',
    'bird':       '000000000285',
    'car':        '000000000632',
    'cat':        '000000000724',
    'horse':      '000000000776',
    'bottle':     '000000000785',
    'chair':      '000000000802',
    'motorcycle': '000000000872',
    'elephant':   '000000001000',
    'giraffe':    '000000091500',
    'zebra':      '000000133000',
    'bear':       '000000151000',
}

COCO_URL = 'http://images.cocodataset.org/val2017/{}.jpg'


def download_coco_images():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = []
    for name, img_id in COCO_IMAGES.items():
        url = COCO_URL.format(img_id)
        dest = INPUT_DIR / f'{name}.jpg'
        if dest.exists():
            print(f"  Ya existe: {dest.name}")
            downloaded.append(dest)
            continue
        print(f"  Descargando {name}...", end=' ')
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            with open(dest, 'wb') as f:
                f.write(resp.content)
            print('OK')
            downloaded.append(dest)
        except Exception as e:
            print(f'Error: {e}')
    return downloaded


def copy_bike():
    bike_source = Path('/home/bellic12/Desktop/Visual/Semana_10_Vision_Computador_Caracteristicas/semana_10_2_coincidencia_patrones_homografias/media/bike.jpg')
    if bike_source.exists():
        dest = INPUT_DIR / 'bike.jpg'
        import shutil
        shutil.copy2(str(bike_source), str(dest))
        print(f"  Copiado: bike.jpg -> {dest}")
        return dest
    else:
        print("  bike.jpg no encontrado en taller vecino")
        return None


def main():
    print("=== Descarga de imagenes de prueba ===")
    print("\nCopiando bike.jpg...")
    copy_bike()
    print("\nDescargando imagenes COCO...")
    images = download_coco_images()
    print(f"\nTotal imagenes disponibles: {len(images)}")
    for img in sorted(INPUT_DIR.iterdir()):
        if img.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            print(f"  - {img.name}")

if __name__ == '__main__':
    main()
