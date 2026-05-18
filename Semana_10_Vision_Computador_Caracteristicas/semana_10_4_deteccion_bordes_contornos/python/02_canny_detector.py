import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import load_image, load_image_rgb, save_and_display, IMAGES


def main():
    print('=== 2. Detector de Bordes de Canny ===\n')

    img_gray = load_image(IMAGES['bike'])
    img_rgb = load_image_rgb(IMAGES['bike'])
    print(f'Imagen cargada: {img_gray.shape[1]}x{img_gray.shape[0]}')

    canny_default = cv2.Canny(img_gray, 100, 200)

    fig, axes = plt.subplots(2, 4, figsize=(20, 10))

    axes[0, 0].imshow(img_rgb)
    axes[0, 0].set_title('Original', fontsize=12)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(canny_default, cmap='gray')
    axes[0, 1].set_title('Canny (umbral bajo=100, alto=200)', fontsize=11)
    axes[0, 1].axis('off')

    sobel_mag = np.sqrt(
        cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)**2 +
        cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)**2
    )
    sobel_mag = np.uint8(np.clip(sobel_mag / sobel_mag.max() * 255, 0, 255))
    _, sobel_thresh = cv2.threshold(sobel_mag, 50, 255, cv2.THRESH_BINARY)
    axes[0, 2].imshow(sobel_thresh, cmap='gray')
    axes[0, 2].set_title('Sobel Magnitud + Umbral (50)', fontsize=11)
    axes[0, 2].axis('off')

    axes[0, 3].axis('off')

    params = [
        ('Bajo=30, Alto=90', 30, 90),
        ('Bajo=50, Alto=150', 50, 150),
        ('Bajo=100, Alto=200', 100, 200),
        ('Bajo=200, Alto=300', 200, 300),
    ]
    for i, (label, low, high) in enumerate(params):
        ax = axes[1, i]
        canny = cv2.Canny(img_gray, low, high)
        ax.imshow(canny, cmap='gray')
        ax.set_title(f'Canny {label}', fontsize=11)
        ax.axis('off')
    plt.tight_layout()
    save_and_display(fig, '02_canny_thresholds.png')

    sigmas = [0.5, 1.0, 1.5, 2.0, 3.0]
    fig2, axes2 = plt.subplots(2, 3, figsize=(18, 10))

    all_images = [(img_rgb, 'Original')]
    for sigma in sigmas:
        ksize = int(2 * round(3 * sigma) + 1)
        if ksize < 3:
            ksize = 3
        blurred = cv2.GaussianBlur(img_gray, (ksize, ksize), sigma)
        canny = cv2.Canny(blurred, 100, 200)
        all_images.append((canny, f'Gauss sigma={sigma}'))

    for i, (im, title) in enumerate(all_images):
        ax = axes2[i // 3, i % 3]
        cm = 'gray' if len(im.shape) == 2 else None
        ax.imshow(im, cmap=cm)
        ax.set_title(title, fontsize=12)
        ax.axis('off')

    plt.tight_layout()
    save_and_display(fig2, '02_canny_gaussian_sigma.png')

    print('Detector Canny aplicado correctamente.')


if __name__ == '__main__':
    main()
