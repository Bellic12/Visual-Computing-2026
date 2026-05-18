import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import (
    load_image, load_image_rgb, save_and_display,
    create_test_image_defects, IMAGES
)


def detect_defects(binary_img, min_area=50):
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    defects = []
    objects = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        hull = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 1.0
        if solidity < 0.9:
            defects.append(c)
        else:
            objects.append(c)
    return objects, defects


def count_objects(binary_img, min_area=50):
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) >= min_area]


def measure_dimensions(contour, pixels_per_mm=1.0):
    x, y, w, h = cv2.boundingRect(contour)
    return {
        'width_mm': w / pixels_per_mm,
        'height_mm': h / pixels_per_mm,
        'area_px': cv2.contourArea(contour),
        'perimeter_px': cv2.arcLength(contour, True),
    }


def classify_by_shape(contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    vertices = len(approx)
    if vertices == 3:
        return 'Triangulo'
    elif vertices == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect = w / float(h) if h > 0 else 0
        if 0.9 <= aspect <= 1.1:
            return 'Cuadrado'
        else:
            return 'Rectangulo'
    elif vertices > 6:
        return 'Circulo'
    else:
        return f'Poligono({vertices})'


def main():
    print('=== 6. Aplicacion de Inspeccion ===\n')

    img_defects = create_test_image_defects()
    img_gray = cv2.cvtColor(img_defects, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)

    objects, defects = detect_defects(binary, min_area=30)
    print(f'Objetos normales: {len(objects)}')
    print(f'Defectos detectados: {len(defects)}')

    img_defect_vis = img_defects.copy()
    cv2.drawContours(img_defect_vis, objects, -1, (0, 255, 0), 2)
    cv2.drawContours(img_defect_vis, defects, -1, (255, 0, 0), 2)
    for d in defects:
        M = cv2.moments(d)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            cv2.putText(img_defect_vis, 'DEFECTO', (cx - 40, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    all_objects = count_objects(binary, min_area=30)
    print(f'Total objetos contados: {len(all_objects)}')

    img_measure = img_defects.copy()
    for c in all_objects:
        dims = measure_dimensions(c)
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(img_measure, (x, y), (x + w, y + h), (0, 255, 255), 2)
        label = f'{dims["width_mm"]:.0f}x{dims["height_mm"]:.0f}'
        cv2.putText(img_measure, label, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        shape_name = classify_by_shape(c)
        cv2.putText(img_measure, shape_name, (x, y + h + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        print(f'  {shape_name}: {dims["width_mm"]:.0f}x{dims["height_mm"]:.0f} px, '
              f'area={dims["area_px"]:.0f}')

    bike_gray = load_image(IMAGES['bike'])
    bike_rgb = load_image_rgb(IMAGES['bike'])
    blurred = cv2.GaussianBlur(bike_gray, (5, 5), 1.5)
    bike_edges = cv2.Canny(blurred, 50, 150)
    bike_contours, _ = cv2.findContours(
        bike_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    bike_filtered = [c for c in bike_contours if cv2.contourArea(c) >= 300]
    img_bike_inspect = bike_rgb.copy()
    classes_bike = {}
    for c in bike_filtered:
        name = classify_by_shape(c)
        classes_bike[name] = classes_bike.get(name, 0) + 1
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(img_bike_inspect, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(img_bike_inspect, name, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    print(f'\nClasificacion en imagen real:')
    for name, count in sorted(classes_bike.items()):
        print(f'  {name}: {count}')

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    axes[0, 0].imshow(img_defects)
    axes[0, 0].set_title('Piezas de prueba (con defectos)', fontsize=12)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(img_defect_vis)
    axes[0, 1].set_title(f'Deteccion de defectos ({len(defects)} encontrados)',
                         fontsize=12)
    axes[0, 1].axis('off')

    axes[1, 0].imshow(img_measure)
    axes[1, 0].set_title('Medicion y clasificacion de formas', fontsize=12)
    axes[1, 0].axis('off')

    ax_table = axes[1, 1]
    ax_table.axis('tight')
    ax_table.axis('off')
    table_data = []
    for i, c in enumerate(all_objects):
        dims = measure_dimensions(c)
        shape = classify_by_shape(c)
        table_data.append([
            str(i + 1), shape,
            f'{dims["width_mm"]:.0f}', f'{dims["height_mm"]:.0f}',
            f'{dims["area_px"]:.0f}'
        ])
    col_labels = ['#', 'Forma', 'Ancho', 'Alto', 'Area (px)']
    ax_table.table(
        cellText=table_data, colLabels=col_labels,
        cellLoc='center', loc='center'
    )
    ax_table.set_title('Resultados de inspeccion', fontsize=12, pad=20)

    plt.tight_layout()
    save_and_display(fig, '06_inspection_defects.png')

    fig2, axes2 = plt.subplots(1, 2, figsize=(16, 7))
    axes2[0].imshow(bike_rgb)
    axes2[0].set_title('Original - bike', fontsize=12)
    axes2[0].axis('off')

    axes2[1].imshow(img_bike_inspect)
    axes2[1].set_title('Inspeccion: bounding boxes + clasificacion', fontsize=12)
    axes2[1].axis('off')

    plt.tight_layout()
    save_and_display(fig2, '06_inspection_bike.png')

    print('\nInspeccion completada.')


if __name__ == '__main__':
    main()
