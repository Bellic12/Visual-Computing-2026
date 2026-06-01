#!/usr/bin/env python3
"""
Taller Clasificación Asistida Texto Imagen Clip.

Compara CLIP (texto + imagen) contra un clasificador tradicional usando
features de ResNet18 y SVM.
"""

import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageFile

import torch
import clip
from torchvision import models
from torchvision.models import ResNet18_Weights
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from tqdm import tqdm


# Permite cargar imágenes con datos incompletos del dataset.
ImageFile.LOAD_TRUNCATED_IMAGES = True


if not hasattr(clip, "load"):
    raise ImportError(
        "Se detectó un paquete 'clip' que no es el de OpenAI. "
        "Desinstala ese paquete e instala la versión oficial: "
        "pip uninstall clip && pip install git+https://github.com/openai/CLIP.git"
    )


DATA_DIR = Path(__file__).parents[1] / "media" / "input" / "toy_dataset"
LABEL_CSV = Path(__file__).parents[1] / "media" / "input" / "toy_dataset_label.csv"
LABEL_COLUMN = "TYPE"
MIN_MUESTRAS_POR_CLASE = 2
OUTPUT_DIR = Path(__file__).parents[1] / "media"
TEST_SIZE = 0.3
MAX_VIS_CLIP = 2
MAX_MUESTRAS_POR_CLASE = 300

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Prompts descriptivos para alinear la terminología de historia del arte
# con el lenguaje natural que entiende CLIP.
PROMPTS_POR_CLASE = {
    "genre": "a classic painting depicting a scene of everyday ordinary life and common people working",
    "other": "an uncategorized artwork, historical artifact, manuscript, or photograph of classical architecture",
    "religious": "a classical painting depicting a religious, divine, or biblical scene",
    "portrait": "a classical portrait painting of a person's face and upper body",
    "landscape": "a landscape painting showing nature, trees, mountains, or countryside",
    "mythological": "a painting depicting ancient mythology, gods, goddesses, or mythical legends",
    "still-life": "a still-life painting of inanimate objects like fruit, flowers, or vessels on a table",
    "study": "an artistic sketch, unfinished draft, or visual study of a subject",
    "historical": "a dramatic painting depicting a significant historical event, battle, or real-world moment",
    "interior": "a painting showing the indoor interior of a room, hall, or building"
}
PROMPT_TEMPLATE = "an artwork depicting {label}"


def listar_imagenes(data_dir: Path, label_csv: Path, label_column: str):
    if not data_dir.exists():
        raise FileNotFoundError(
            f"No existe el directorio de datos: {data_dir}. "
            "Verifica la ruta de las imagenes."
        )

    if not label_csv.exists():
        raise FileNotFoundError(
            f"No existe el archivo CSV de labels: {label_csv}."
        )

    samples = []
    counts = {}
    with label_csv.open("r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file, delimiter="\t")
        if not reader.fieldnames or "FILE" not in reader.fieldnames:
            raise ValueError("El CSV no contiene la columna FILE.")
        if label_column not in reader.fieldnames:
            columnas = ", ".join(reader.fieldnames)
            raise ValueError(
                f"La columna {label_column} no existe. Disponibles: {columnas}"
            )

        for row in reader:
            file_name = (row.get("FILE") or "").strip()
            label = (row.get(label_column) or "").strip()
            if not file_name or not label:
                continue

            img_path = data_dir / file_name
            if img_path.suffix.lower() not in IMAGE_EXTS:
                continue
            if not img_path.exists():
                continue

            # Limita el número de muestras por clase.
            if counts.get(label, 0) >= MAX_MUESTRAS_POR_CLASE:
                continue

            samples.append((img_path, label))
            counts[label] = counts.get(label, 0) + 1

    if not samples:
        raise ValueError(
            "No se encontraron pares imagen/label. Verifica el CSV y la ruta."
        )

    labels_validos = {
        label for label, count in counts.items() if count >= MIN_MUESTRAS_POR_CLASE
    }
    samples = [sample for sample in samples if sample[1] in labels_validos]

    if not samples:
        raise ValueError(
            "No hay clases con suficientes muestras para entrenar. "
            "Ajusta MIN_MUESTRAS_POR_CLASE."
        )

    class_names = sorted(labels_validos)
    class_to_idx = {name: idx for idx, name in enumerate(class_names)}
    labels = [class_to_idx[label] for _, label in samples]

    return class_names, samples, labels


def obtener_prompts(class_names):
    prompts = []
    for name in class_names:
        if name in PROMPTS_POR_CLASE:
            prompts.append(PROMPTS_POR_CLASE[name])
        else:
            label = name.replace("_", " ").lower()
            prompts.append(PROMPT_TEMPLATE.format(label=label))
    return prompts


def predecir_clip(model, preprocess, image_paths, text_prompts, device, progress=None):
    text_inputs = clip.tokenize(text_prompts).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    probs = []
    for img_path in image_paths:
        image = preprocess(Image.open(img_path).convert("RGB")).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = model.encode_image(image)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            logits = (100.0 * image_features @ text_features.T).squeeze(0)
            prob = logits.softmax(dim=-1).cpu().numpy()
        probs.append(prob)
        if progress is not None:
            progress.update(1)

    return np.vstack(probs)


def guardar_visuales_clip(output_dir, image_paths, class_names, probs, preds):
    output_dir.mkdir(parents=True, exist_ok=True)

    limite = min(MAX_VIS_CLIP, len(image_paths))
    for idx in range(limite):
        img_path = image_paths[idx]
        prob = probs[idx]
        pred_idx = preds[idx]

        img = Image.open(img_path).convert("RGB")
        fig, axes = plt.subplots(1, 2, figsize=(8, 4))

        axes[0].imshow(img)
        axes[0].set_title(f"Prediccion: {class_names[pred_idx]}")
        axes[0].axis("off")

        axes[1].barh(class_names, prob)
        axes[1].set_xlim(0, 1)
        axes[1].set_xlabel("Confianza")
        axes[1].invert_yaxis()

        fig.tight_layout()
        fig.savefig(output_dir / f"clip_resultado_{idx + 1}.svg")
        plt.close(fig)


def extraer_features(resnet, transform, image_paths, device, progress=None):
    features = []
    for img_path in image_paths:
        image = transform(Image.open(img_path).convert("RGB")).unsqueeze(0).to(device)
        with torch.no_grad():
            feat = resnet(image).squeeze(0).cpu().numpy()
        features.append(feat)
        if progress is not None:
            progress.update(1)

    return np.vstack(features)


def main():
    class_names, samples, labels = listar_imagenes(DATA_DIR, LABEL_CSV, LABEL_COLUMN)
    prompts = obtener_prompts(class_names)

    train_samples, test_samples, train_labels, test_labels = train_test_split(
        samples,
        labels,
        test_size=TEST_SIZE,
        random_state=42,
        stratify=labels,
    )

    train_paths = [s[0] for s in train_samples]
    test_paths = [s[0] for s in test_samples]

    device = "cuda" if torch.cuda.is_available() else "cpu"

    registro_csv = OUTPUT_DIR / "registro_dataset.csv"
    with open(registro_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Fase", "Clase_Real", "Nombre_Archivo"])

        for sample, label_idx in zip(train_samples, train_labels):
            img_path = sample[0]
            clase = class_names[label_idx]
            writer.writerow(["Train", clase, img_path.name])

        for sample, label_idx in zip(test_samples, test_labels):
            img_path = sample[0]
            clase = class_names[label_idx]
            writer.writerow(["Test", clase, img_path.name])

    print(f"\n[+] Registro del dataset guardado en: {registro_csv}")

    print("\n--- IMÁGENES USADAS EN LOS GRÁFICOS CLIP ---")
    limite = min(MAX_VIS_CLIP, len(test_paths))
    for i in range(limite):
        print(f"  El archivo clip_resultado_{i+1}.svg usó: {test_paths[i].name}")
    print("--------------------------------------------\n")

    total_imgs = len(test_paths) + len(train_paths) + len(test_paths)
    extra_steps = 4
    with tqdm(total=total_imgs + extra_steps, desc="Progreso", unit="img") as progress:
        # Parte 1: CLIP
        progress.set_description("CLIP")
        clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
        clip_model.eval()

        clip_probs = predecir_clip(
            clip_model, clip_preprocess, test_paths, prompts, device, progress
        )
        clip_preds = clip_probs.argmax(axis=1)
        clip_acc = accuracy_score(test_labels, clip_preds)

        guardar_visuales_clip(OUTPUT_DIR, test_paths, class_names, clip_probs, clip_preds)

        # Parte 2: Clasificador tradicional con features de ResNet
        progress.set_description("ResNet")
        weights = ResNet18_Weights.DEFAULT
        resnet = models.resnet18(weights=weights)
        resnet.fc = torch.nn.Identity()
        resnet.eval()
        resnet.to(device)

        resnet_transform = weights.transforms()

        progress.set_description("ResNet (train)")
        train_feats = extraer_features(resnet, resnet_transform, train_paths, device, progress)
        progress.set_description("ResNet (test)")
        test_feats = extraer_features(resnet, resnet_transform, test_paths, device, progress)

        progress.set_description("SVM (entrenamiento)")
        clf = SVC(kernel="linear", class_weight="balanced")
        clf.fit(train_feats, train_labels)
        progress.update(1)

        progress.set_description("SVM (evaluacion)")
        trad_preds = clf.predict(test_feats)
        trad_acc = accuracy_score(test_labels, trad_preds)
        progress.update(1)

        progress.set_description("Graficas (matriz)")
        cm = confusion_matrix(test_labels, trad_preds, labels=list(range(len(class_names))))

        fig, ax = plt.subplots(figsize=(8, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)

        disp.plot(cmap="Blues", values_format="d", ax=ax, xticks_rotation=45)

        plt.title("Matriz de confusion - Tradicional")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "tradicional_resultado_1.svg")
        plt.close()
        progress.update(1)

        progress.set_description("Graficas (comparacion)")
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(["CLIP", "Tradicional"], [clip_acc, trad_acc], color=["#1f77b4", "#ff7f0e"])
        ax.set_ylim(0, 1)
        ax.set_ylabel("Exactitud")
        ax.set_title("Comparacion de exactitud")
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "tradicional_resultado_2.svg")
        plt.close(fig)
        progress.update(1)

    print(f"Exactitud CLIP: {clip_acc:.3f}")
    print(f"Exactitud Tradicional: {trad_acc:.3f}")
    print(f"Visuales guardados en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
