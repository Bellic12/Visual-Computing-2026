import requests
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import INPUT_DIR, MEDIA_DIR

COCO_IMAGES = [
    ('img_01', '000000151000'),
    ('img_02', '000000000139'),
    ('img_03', '000000000285'),
    ('img_04', '000000000785'),
    ('img_05', '000000000632'),
    ('img_06', '000000000724'),
    ('img_07', '000000000802'),
    ('img_08', '000000001000'),
    ('img_09', '000000091500'),
    ('img_10', '000000000776'),
    ('img_11', '000000000872'),
    ('img_12', '000000133000'),
    ('img_13', '000000000633'),
]

COCO_URL = 'http://images.cocodataset.org/val2017/{}.jpg'


def download_coco_images():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = []
    for name, img_id in COCO_IMAGES:
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


def copy_images():
    import shutil
    sources = {
        'img_02.jpg': Path('/home/bellic12/Desktop/Visual/Semana_10_Vision_Computador_Caracteristicas/semana_10_2_coincidencia_patrones_homografias/media/bike.jpg'),
    }
    for name, src in sources.items():
        if src.exists():
            dest = INPUT_DIR / name
            shutil.copy2(str(src), str(dest))
            print(f"  Copiado: {src.name} -> {dest}")
        else:
            print(f"  No encontrado: {src}")


def main():
    print("=== Descarga de imagenes de prueba ===")
    print("\nCopiando imagenes desde talleres vecinos...")
    copy_images()
    print("\nDescargando imagenes COCO...")
    images = download_coco_images()
    print(f"\nTotal imagenes disponibles: {len(images)}")
    for img in sorted(INPUT_DIR.iterdir()):
        if img.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            print(f"  - {img.name}")

if __name__ == '__main__':
    main()
