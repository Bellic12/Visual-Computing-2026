import torch
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import cv2
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MODEL_PATH = '../notebooks/parking_lot_detector.pth'
IMAGE_PATH = '../notebooks/some_test_images/t1.jpg'
TARGET_SIZE = 640

# ROI points (área de interés para centrar la detección)
ROI_POINTS = np.array([[50, 85], [510, 75], [524, 165], [20, 175]], dtype=np.float32)

# Dimensiones del mundo real (meters)
REAL_WIDTH = 76.0
REAL_HEIGHT = 13.5

# Umbral de confianza para detecciones
THRESHOLD = 0.5

#-------------------------------------------
# FUNCIONES DEL MODELO
#-------------------------------------------

# Cargar modelo el preentrenado Resnet50 
def load_model():
    # model = fasterrcnn_resnet50_fpn(pretrained=False)
    model = fasterrcnn_resnet50_fpn(weights = None, weights_backbone = None)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, 3)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE).eval()
    return model

print("Cargando modelo...")
model = load_model()

# Detección de vehículos 
@torch.no_grad()
def detect(model, image):
    img_tensor = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0).to(DEVICE)
    pred = model(img_tensor)[0]
    keep = pred['scores'] > THRESHOLD
    return pred['boxes'][keep].cpu().numpy(), pred['labels'][keep].cpu().numpy(), pred['scores'][keep].cpu().numpy()

# -------------------------------------------
# FUNCIONES DE LAS TRANSFORMACIONES
# -------------------------------------------
def perspective_transform(image, roi_points):
    """Aplica homografía y padding para mantener 640x640"""
    # Calcular dimensiones del rectángulo destino (ROI)
    top_w = np.linalg.norm(roi_points[1] - roi_points[0])
    bottom_w = np.linalg.norm(roi_points[2] - roi_points[3])
    left_h = np.linalg.norm(roi_points[3] - roi_points[0])
    right_h = np.linalg.norm(roi_points[2] - roi_points[1])
    avg_w, avg_h = (top_w + bottom_w) / 2, (left_h + right_h) / 2

    aspect_ratio = avg_w / avg_h
    dest_w = TARGET_SIZE if aspect_ratio > 1 else int(TARGET_SIZE * aspect_ratio)
    dest_h = int(TARGET_SIZE / aspect_ratio) if aspect_ratio > 1 else TARGET_SIZE

    # Homografía (transformación de perspectiva)
    dst_points = np.array([[0, 0], [dest_w-1, 0], [dest_w-1, dest_h-1], [0, dest_h-1]], dtype=np.float32)
    h_matrix = cv2.getPerspectiveTransform(roi_points, dst_points)
    warped = cv2.warpPerspective(image, h_matrix, (dest_w, dest_h))

    # Padding a 640x640 para mantener las dimensiones (mejora la detección de Resnet50)
    scale = min(TARGET_SIZE / dest_w, TARGET_SIZE / dest_h)
    new_w, new_h = int(dest_w * scale), int(dest_h * scale)
    resized = cv2.resize(warped, (new_w, new_h))

    padded = np.zeros((TARGET_SIZE, TARGET_SIZE, 3), dtype=np.float32)
    offset_x, offset_y = (TARGET_SIZE - new_w) // 2, (TARGET_SIZE - new_h) // 2
    padded[offset_y:offset_y+new_h, offset_x:offset_x+new_w] = resized

    return padded, h_matrix, scale, (offset_x, offset_y), (dest_w, dest_h)

def convert_to_real_coords(boxes, labels, scores, offset, dest_size):
    """Convierte coordenadas a metros reales (solo ocupados)"""
    dest_w, dest_h = dest_size
    px_to_m_x, px_to_m_y = REAL_WIDTH / dest_w, REAL_HEIGHT / (dest_h)

    coords = []
    for box, label, score in zip(boxes, labels, scores):
        if label == 2:  # Solo ocupados
            # Centro de la bounding box
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            cxM = (cx - offset[0]) * px_to_m_x
            cyM = (cy - offset[1]) * px_to_m_y

            coords.append((round(cxM, 4), round(cyM, 4)))
    return coords

# -------------------------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------------------------
def main():
    # Cargar modelo

    # Cargar imagen
    img = cv2.imread(IMAGE_PATH)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_float = img_rgb.astype(np.float32) / 255.0

    # Transformar
    padded, h_matrix, scale, offset, dest_size = perspective_transform(img_float, ROI_POINTS)

    # Detectar
    boxes, labels, scores = detect(model, padded)

    # Convertir a coordenadas reales
    real_coords = convert_to_real_coords(boxes, labels, scores, offset, dest_size)

    # Imprimir resultados
    print("Coordenadas de los vehículos detectados:")
    for i, (x, y) in enumerate(real_coords):
        print(f"  Vehículo {i+1}: X={x:.4f}m, Y={y:.4f}m")
    print(f"\nTotal vehículos: {len(real_coords)}")

    # # VISUALIZACION DEL PASO A PASO: descomentar para ver cada etapa del proceso
    # fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # # 1. Original con ROI
    # img_vis = img_rgb.copy()
    # cv2.polylines(img_vis, [ROI_POINTS.astype(np.int32)], True, (0, 255, 0), 3)
    # for p in ROI_POINTS:
    #     cv2.circle(img_vis, (int(p[0]), int(p[1])), 6, (0, 255, 0), -1)
    # axes[0, 0].imshow(img_vis)
    # axes[0, 0].set_title("1. Imagen original con ROI")
    # axes[0, 0].axis('off')

    # # 2. ROI transformado (sin padding)
    # warped = cv2.warpPerspective(img_float, h_matrix, (dest_size[0], dest_size[1]))
    # axes[0, 1].imshow((warped * 255).astype(np.uint8))
    # axes[0, 1].set_title(f"2. ROI transformado ({dest_size[0]}x{dest_size[1]})")
    # axes[0, 1].axis('off')

    # # 3. ROI con padding
    # axes[1, 0].imshow((padded * 255).astype(np.uint8))
    # axes[1, 0].set_title("3. ROI con padding (640x640)")
    # axes[1, 0].axis('off')

    # # 4. Detecciones en ROI con padding
    # img_det = (padded * 255).astype(np.uint8).copy()
    # for box, label, score in zip(boxes, labels, scores):
    #     if label == 2:
    #         x1, y1, x2, y2 = map(int, box)
    #         cv2.rectangle(img_det, (x1, y1), (x2, y2), (0, 0, 255), 2)
    #         cv2.putText(img_det, f"{score:.2f}", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    # axes[1, 1].imshow(img_det)
    # axes[1, 1].set_title(f"4. Detecciones ({len(real_coords)} vehículos)")
    # axes[1, 1].axis('off')
    # cv2.imwrite('imagen_copia.jpg', img_det)

    # plt.tight_layout()
    # plt.savefig('pipeline_result.png', dpi=150)
    # plt.show()

    return real_coords

if __name__ == "__main__":
    coords = main()