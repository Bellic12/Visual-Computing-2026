import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import filters
from utils import load_image, load_image_rgb, save_and_display, IMAGES


def main():
    print('=== 1. Operadores basicos de deteccion de bordes ===\n')

    img_gray = load_image(IMAGES['bike'])
    img_rgb = load_image_rgb(IMAGES['bike'])
    print(f'Imagen cargada: {img_gray.shape[1]}x{img_gray.shape[0]}')

    img_float = img_gray.astype(np.float32) / 255.0

    sobel_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_mag = np.sqrt(sobel_x**2 + sobel_y**2)
    sobel_mag = np.uint8(np.clip(sobel_mag / sobel_mag.max() * 255, 0, 255))

    prewitt_x = filters.prewitt_h(img_float)
    prewitt_y = filters.prewitt_v(img_float)
    prewitt_mag = np.sqrt(prewitt_x**2 + prewitt_y**2)
    prewitt_mag = np.uint8(np.clip(prewitt_mag / prewitt_mag.max() * 255, 0, 255))

    laplacian = cv2.Laplacian(img_gray, cv2.CV_64F, ksize=3)
    laplacian = np.uint8(np.clip(np.abs(laplacian) / np.abs(laplacian).max() * 255, 0, 255))

    scharr_x = cv2.Scharr(img_gray, cv2.CV_64F, 1, 0)
    scharr_y = cv2.Scharr(img_gray, cv2.CV_64F, 0, 1)
    scharr_mag = np.sqrt(scharr_x**2 + scharr_y**2)
    scharr_mag = np.uint8(np.clip(scharr_mag / scharr_mag.max() * 255, 0, 255))

    fig, axes = plt.subplots(4, 4, figsize=(18, 20))

    axes[0, 0].imshow(img_rgb)
    axes[0, 0].set_title('Original', fontsize=12)
    axes[0, 0].axis('off')

    axes[0, 1].axis('off')
    axes[0, 2].axis('off')
    axes[0, 3].axis('off')

    titles = ['Sobel X', 'Sobel Y', 'Sobel Magnitud', 'Sobel (X+Y)']
    sobel_list = [
        cv2.convertScaleAbs(sobel_x),
        cv2.convertScaleAbs(sobel_y),
        sobel_mag,
        cv2.addWeighted(cv2.convertScaleAbs(sobel_x), 0.5,
                        cv2.convertScaleAbs(sobel_y), 0.5, 0)
    ]
    for i, (img, title) in enumerate(zip(sobel_list, titles)):
        ax = axes[1, i]
        ax.imshow(img, cmap='gray')
        ax.set_title(title, fontsize=12)
        ax.axis('off')

    prewitt_list = [
        np.uint8(np.clip(np.abs(prewitt_x) * 255, 0, 255)),
        np.uint8(np.clip(np.abs(prewitt_y) * 255, 0, 255)),
        prewitt_mag,
        np.uint8(np.clip((np.abs(prewitt_x) + np.abs(prewitt_y)) * 128, 0, 255))
    ]
    titles_p = ['Prewitt X', 'Prewitt Y', 'Prewitt Magnitud', 'Prewitt (X+Y)']
    for i, (img, title) in enumerate(zip(prewitt_list, titles_p)):
        ax = axes[2, i]
        ax.imshow(img, cmap='gray')
        ax.set_title(title, fontsize=12)
        ax.axis('off')

    axes[3, 0].imshow(laplacian, cmap='gray')
    axes[3, 0].set_title('Laplaciano', fontsize=12)
    axes[3, 0].axis('off')

    axes[3, 1].imshow(scharr_mag, cmap='gray')
    axes[3, 1].set_title('Scharr Magnitud', fontsize=12)
    axes[3, 1].axis('off')

    axes[3, 2].imshow(cv2.convertScaleAbs(scharr_x), cmap='gray')
    axes[3, 2].set_title('Scharr X', fontsize=12)
    axes[3, 2].axis('off')

    axes[3, 3].imshow(cv2.convertScaleAbs(scharr_y), cmap='gray')
    axes[3, 3].set_title('Scharr Y', fontsize=12)
    axes[3, 3].axis('off')

    plt.tight_layout()
    save_and_display(fig, '01_edge_operators_comparison.png')

    fig2, axes2 = plt.subplots(2, 4, figsize=(20, 10))
    operadores = [
        ('Sobel X', cv2.convertScaleAbs(sobel_x)),
        ('Sobel Y', cv2.convertScaleAbs(sobel_y)),
        ('Sobel Mag', sobel_mag),
        ('Laplaciano', laplacian),
        ('Prewitt Mag', prewitt_mag),
        ('Scharr Mag', scharr_mag),
        ('Scharr X', cv2.convertScaleAbs(scharr_x)),
        ('Scharr Y', cv2.convertScaleAbs(scharr_y)),
    ]
    for i, (title, img) in enumerate(operadores):
        ax = axes2[i // 4, i % 4]
        ax.imshow(img, cmap='gray')
        ax.set_title(title, fontsize=12)
        ax.axis('off')

    plt.tight_layout()
    save_and_display(fig2, '01_edge_operators_grid.png')

    print('Operadores de borde aplicados correctamente.')


if __name__ == '__main__':
    main()
