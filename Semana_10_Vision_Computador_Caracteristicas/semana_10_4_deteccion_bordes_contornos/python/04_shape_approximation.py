import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import (
    load_image, load_image_rgb, save_and_display,
    create_test_image_shapes, IMAGES
)


def classify_shape(vertices):
    if len(vertices) == 3:
        return 'Triangulo'
    elif len(vertices) == 4:
        x, y, w, h = cv2.boundingRect(vertices)
        aspect = w / float(h)
        if 0.9 <= aspect <= 1.1:
            return 'Cuadrado'
        else:
            return 'Rectangulo'
    elif len(vertices) == 5:
        return 'Pentagono'
    elif len(vertices) == 6:
        return 'Hexagono'
    else:
        return 'Circulo'


def main():
    print('=== 4. Aproximacion de Formas ===\n')

    img_shapes = create_test_image_shapes()
    img_gray = cv2.cvtColor(img_shapes, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f'Formas detectadas: {len(contours)}')

    bike_gray = load_image(IMAGES['bike'])
    bike_rgb = load_image_rgb(IMAGES['bike'])
    blurred = cv2.GaussianBlur(bike_gray, (5, 5), 1.5)
    bike_edges = cv2.Canny(blurred, 50, 150)
    bike_contours, _ = cv2.findContours(
        bike_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    img_result = img_shapes.copy()
    img_classified = img_shapes.copy()

    colors = {
        'Triangulo': (255, 0, 0),
        'Cuadrado': (0, 255, 0),
        'Rectangulo': (0, 0, 255),
        'Circulo': (255, 255, 0),
        'Pentagono': (255, 0, 255),
        'Hexagono': (0, 255, 255),
    }

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        epsilon = 0.02 * peri
        approx = cv2.approxPolyDP(contour, epsilon, True)

        area = cv2.contourArea(contour)
        vertices = len(approx)
        shape_name = classify_shape(approx)

        cv2.drawContours(img_result, [approx], -1, (0, 200, 0), 2)
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.putText(img_result, f'{vertices}v', (cx - 20, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        color = colors.get(shape_name, (128, 128, 128))
        cv2.drawContours(img_classified, [approx], -1, color, 3)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.putText(img_classified, shape_name, (cx - 30, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        print(f'  {shape_name}: vertices={vertices}, area={area:.1f}, '
              f'perimetro={peri:.1f}')

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    axes[0, 0].imshow(img_shapes)
    axes[0, 0].set_title('Imagen de formas sintetica', fontsize=12)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(img_result)
    axes[0, 1].set_title('Contornos aproximados (poligonos)', fontsize=12)
    axes[0, 1].axis('off')

    axes[1, 0].imshow(img_classified)
    axes[1, 0].set_title('Formas clasificadas', fontsize=12)
    axes[1, 0].axis('off')

    bike_result = bike_rgb.copy()
    for c in bike_contours:
        if cv2.contourArea(c) < 500:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        cv2.drawContours(bike_result, [approx], -1, (0, 255, 0), 2)

    axes[1, 1].imshow(bike_result)
    axes[1, 1].set_title('Aproximacion en imagen real (bike)', fontsize=12)
    axes[1, 1].axis('off')

    plt.tight_layout()
    save_and_display(fig, '04_shape_approximation.png')

    print('Aproximacion de formas completada.')


if __name__ == '__main__':
    main()
