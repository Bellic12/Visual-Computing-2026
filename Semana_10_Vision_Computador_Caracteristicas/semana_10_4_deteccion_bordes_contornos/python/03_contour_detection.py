import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import load_image, load_image_rgb, save_and_display, IMAGES


def main():
    print('=== 3. Deteccion de Contornos ===\n')

    img_gray = load_image(IMAGES['bike'])
    img_rgb = load_image_rgb(IMAGES['bike'])
    print(f'Imagen cargada: {img_gray.shape[1]}x{img_gray.shape[0]}')

    blurred = cv2.GaussianBlur(img_gray, (5, 5), 1.5)
    edges = cv2.Canny(blurred, 50, 150)

    contours, hierarchy = cv2.findContours(
        edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    print(f'Contornos encontrados (RETR_TREE): {len(contours)}')

    img_all = img_rgb.copy()
    cv2.drawContours(img_all, contours, -1, (0, 255, 0), 2)

    img_ext = img_rgb.copy()
    contours_ext, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cv2.drawContours(img_ext, contours_ext, -1, (0, 255, 0), 2)
    print(f'Contornos externos (RETR_EXTERNAL): {len(contours_ext)}')

    adaptive = cv2.adaptiveThreshold(
        img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    contours_adapt, _ = cv2.findContours(
        adaptive, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    img_adapt = img_rgb.copy()
    cv2.drawContours(img_adapt, contours_adapt, -1, (0, 255, 0), 2)
    print(f'Contornos (umbral adaptativo): {len(contours_adapt)}')

    min_area = 500
    filtered = [c for c in contours_ext if cv2.contourArea(c) >= min_area]
    img_filt = img_rgb.copy()
    cv2.drawContours(img_filt, filtered, -1, (0, 255, 0), 2)
    print(f'Contornos filtrados (area >= {min_area}): {len(filtered)}')

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))

    axes[0, 0].imshow(img_rgb)
    axes[0, 0].set_title('Original', fontsize=12)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(edges, cmap='gray')
    axes[0, 1].set_title('Bordes Canny', fontsize=12)
    axes[0, 1].axis('off')

    axes[0, 2].imshow(img_all)
    axes[0, 2].set_title(f'Todos los contornos ({len(contours)})', fontsize=12)
    axes[0, 2].axis('off')

    axes[1, 0].imshow(img_ext)
    axes[1, 0].set_title(f'Contornos externos ({len(contours_ext)})', fontsize=12)
    axes[1, 0].axis('off')

    axes[1, 1].imshow(adaptive, cmap='gray')
    axes[1, 1].set_title('Umbral adaptativo', fontsize=12)
    axes[1, 1].axis('off')

    axes[1, 2].imshow(img_filt)
    axes[1, 2].set_title(f'Filtrados area>={min_area} ({len(filtered)})', fontsize=12)
    axes[1, 2].axis('off')

    plt.tight_layout()
    save_and_display(fig, '03_contour_detection.png')

    if hierarchy is not None:
        print(f'\nJerarquia de contornos (primeros 5):')
        for i in range(min(5, len(contours))):
            h = hierarchy[0][i]
            print(f'  Contorno {i}: next={h[0]}, prev={h[1]}, child={h[2]}, parent={h[3]}')

    print('\nDeteccion de contornos completada.')


if __name__ == '__main__':
    main()
