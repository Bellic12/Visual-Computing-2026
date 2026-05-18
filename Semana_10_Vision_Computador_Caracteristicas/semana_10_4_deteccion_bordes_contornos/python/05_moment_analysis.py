import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import (
    load_image, load_image_rgb, save_and_display,
    create_test_image_shapes, IMAGES
)


def main():
    print('=== 5. Analisis de Momentos ===\n')

    img_shapes = create_test_image_shapes()
    img_gray = cv2.cvtColor(img_shapes, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f'Formas detectadas: {len(contours)}')

    img_centroids = img_shapes.copy()
    img_orientation = img_shapes.copy()

    data_rows = []
    for i, c in enumerate(contours):
        M = cv2.moments(c)
        area = M['m00']
        if area == 0:
            continue

        cx = int(M['m10'] / area)
        cy = int(M['m01'] / area)

        mu20 = M['mu20'] / area
        mu02 = M['mu02'] / area
        mu11 = M['mu11'] / area

        theta = 0.5 * np.arctan2(2 * mu11, mu20 - mu02)
        theta_deg = np.degrees(theta)

        a = mu20 + mu02
        b = np.sqrt(4 * mu11**2 + (mu20 - mu02)**2)
        eccentricity = np.sqrt(1 - (a - b) / (a + b)) if (a + b) > 0 else 0

        cv2.circle(img_centroids, (cx, cy), 5, (255, 0, 0), -1)
        cv2.putText(img_centroids, f'{i}', (cx + 10, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        length = 50
        end_x = int(cx + length * np.cos(theta))
        end_y = int(cy + length * np.sin(theta))
        cv2.arrowedLine(img_orientation, (cx, cy), (end_x, end_y),
                        (0, 0, 255), 2, tipLength=0.2)
        cv2.circle(img_orientation, (cx, cy), 5, (255, 0, 0), -1)
        cv2.putText(img_orientation, f'{i}', (cx + 10, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        data_rows.append({
            'idx': i,
            'area': area,
            'centroide': f'({cx}, {cy})',
            'orientacion_deg': theta_deg,
            'excentricidad': eccentricity
        })
        print(f'  Forma {i}: area={area:.1f}, centroide=({cx},{cy}), '
              f'orientacion={theta_deg:.1f} deg, excentricidad={eccentricity:.3f}')

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    axes[0, 0].imshow(img_shapes)
    axes[0, 0].set_title('Imagen original de formas', fontsize=12)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(img_centroids)
    axes[0, 1].set_title('Centroides detectados', fontsize=12)
    axes[0, 1].axis('off')

    axes[1, 0].imshow(img_orientation)
    axes[1, 0].set_title('Centroides + Orientacion', fontsize=12)
    axes[1, 0].axis('off')

    ax_table = axes[1, 1]
    ax_table.axis('tight')
    ax_table.axis('off')
    table_data = [
        [str(r['idx']), f'{r["area"]:.0f}', r['centroide'],
         f'{r["orientacion_deg"]:.1f}', f'{r["excentricidad"]:.3f}']
        for r in data_rows
    ]
    col_labels = ['Forma', 'Area', 'Centroide', 'Orientacion (deg)', 'Excentricidad']
    table = ax_table.table(
        cellText=table_data, colLabels=col_labels,
        cellLoc='center', loc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    plt.tight_layout()
    save_and_display(fig, '05_moment_analysis.png')

    bike_gray = load_image(IMAGES['bike'])
    bike_rgb = load_image_rgb(IMAGES['bike'])
    blurred = cv2.GaussianBlur(bike_gray, (5, 5), 1.5)
    bike_edges = cv2.Canny(blurred, 50, 150)
    bike_contours, _ = cv2.findContours(
        bike_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    fig2, axes2 = plt.subplots(1, 2, figsize=(16, 7))
    axes2[0].imshow(bike_rgb)
    axes2[0].set_title('Original', fontsize=12)
    axes2[0].axis('off')

    bike_moments = bike_rgb.copy()
    for c in bike_contours:
        if cv2.contourArea(c) < 300:
            continue
        M = cv2.moments(c)
        if M['m00'] == 0:
            continue
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        cv2.circle(bike_moments, (cx, cy), 4, (255, 0, 0), -1)

    axes2[1].imshow(bike_moments)
    axes2[1].set_title('Centroides en imagen real', fontsize=12)
    axes2[1].axis('off')

    plt.tight_layout()
    save_and_display(fig2, '05_moment_analysis_bike.png')

    print('Analisis de momentos completado.')


if __name__ == '__main__':
    main()
