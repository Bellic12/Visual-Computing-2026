"""
CLIP Batch Classification - Bonus script (Taller Semana 12.2)
Classifies multiple images in a single forward pass and explores
cross-modal embeddings with progressively specific label hierarchies.
"""

import os
import sys
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

try:
    import clip
    import torch
except ImportError:
    print("Install CLIP first: pip install git+https://github.com/openai/CLIP.git")
    sys.exit(1)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR  = os.path.join(BASE_DIR, "..", "media")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
DEVICE     = "cuda" if torch.cuda.is_available() else "cpu"

os.makedirs(MEDIA_DIR, exist_ok=True)


# -- Core -------------------------------------------------------------------

def load_model():
    print(f"Loading CLIP ViT-B/32 on {DEVICE.upper()}...")
    model, preprocess = clip.load("ViT-B/32", device=DEVICE)
    model.eval()
    print("Ready.\n")
    return model, preprocess


def find_image(name_no_ext):
    for ext in (".jpg", ".jpeg", ".png"):
        p = os.path.join(IMAGES_DIR, name_no_ext + ext)
        if os.path.exists(p):
            return p
    return None


def batch_classify(model, preprocess, image_paths, labels):
    """One forward pass for N images x M labels -> (N, M) probability matrix."""
    images = torch.stack([
        preprocess(Image.open(p).convert("RGB")) for p in image_paths
    ]).to(DEVICE)
    tokens = clip.tokenize(labels).to(DEVICE)

    with torch.no_grad():
        logits, _ = model(images, tokens)
        probs = logits.softmax(dim=-1).cpu().numpy()
    return probs


def classify_single(model, preprocess, image_path, labels):
    return batch_classify(model, preprocess, [image_path], labels)[0]


# -- Demo 1: Batch classification of all available images ------------------

def run_batch_demo(model, preprocess):
    print("=" * 58)
    print("BONUS DEMO 1 - Batch Classification (all images)")
    print("=" * 58)

    paths = sorted(
        glob.glob(os.path.join(IMAGES_DIR, "*.jpg")) +
        glob.glob(os.path.join(IMAGES_DIR, "*.jpeg")) +
        glob.glob(os.path.join(IMAGES_DIR, "*.png"))
    )
    if not paths:
        print("  No images found in images/")
        return

    general_labels = [
        "an animal",
        "a vehicle or machine",
        "food",
        "a natural landscape",
        "a human or person",
    ]

    print(f"\nImages: {len(paths)}   Labels: {general_labels}\n")
    all_probs = batch_classify(model, preprocess, paths, general_labels)

    for path, probs in zip(paths, all_probs):
        best = general_labels[int(np.argmax(probs))]
        name = os.path.basename(path)
        print(f"  {name:<22}  ->  \"{best}\"  ({np.max(probs)*100:.1f}%)")

    # Visualise up to 4 images
    vis_paths = paths[:4]
    vis_probs = all_probs[:4]
    n = len(vis_paths)

    fig, axes = plt.subplots(n, 2, figsize=(13, 4 * n))
    if n == 1:
        axes = [axes]
    fig.suptitle("CLIP Batch Classification", fontsize=14, fontweight="bold")

    for i, (p, probs) in enumerate(zip(vis_paths, vis_probs)):
        best_i = int(np.argmax(probs))
        axes[i][0].imshow(Image.open(p).convert("RGB"))
        axes[i][0].axis("off")
        axes[i][0].set_title(
            f"{os.path.basename(p)}\n-> \"{general_labels[best_i]}\"",
            fontsize=9, color="#27AE60", fontweight="bold"
        )
        cols = ["#27AE60" if j == best_i else "#2980B9" for j in range(len(general_labels))]
        axes[i][1].barh(general_labels, probs * 100, color=cols)
        axes[i][1].set_xlabel("Probability (%)")
        axes[i][1].set_xlim(0, 110)
        for j, pr in enumerate(probs):
            axes[i][1].text(pr * 100 + 1, j, f"{pr*100:.1f}%", va="center", fontsize=8)

    plt.tight_layout()
    out = os.path.join(MEDIA_DIR, "result_batch.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved -> media/result_batch.png")


# -- Demo 2: Progressively specific label hierarchy ------------------------

HIERARCHY = {
    "L1 - Kingdom":  ["living thing",  "non-living thing"],
    "L2 - Category": ["animal",  "plant",  "vehicle",  "food",  "building"],
    "L3 - Family":   ["dog",  "cat",  "bird",  "fish",  "reptile"],
    "L4 - Breed":    [
        "a yellow Labrador dog",
        "a black and white cat",
        "a small brown sparrow",
        "a tropical fish",
        "a green iguana",
    ],
}


def run_hierarchy_demo(model, preprocess):
    print("\n" + "=" * 58)
    print("BONUS DEMO 2 - Progressive Label Hierarchy")
    print("=" * 58)

    img_path = find_image("dog")
    if img_path is None:
        print("  Skipping (dog image not found)")
        return

    n_levels = len(HIERARCHY)
    fig, axes = plt.subplots(1, n_levels + 1, figsize=(5 * (n_levels + 1), 5))
    fig.suptitle("CLIP Hierarchical Label Specificity - dog",
                 fontsize=13, fontweight="bold")

    axes[0].imshow(Image.open(img_path).convert("RGB"))
    axes[0].axis("off")
    axes[0].set_title("Input", fontsize=10)

    for ax, (level_name, labels) in zip(axes[1:], HIERARCHY.items()):
        probs = classify_single(model, preprocess, img_path, labels)
        best_i = int(np.argmax(probs))
        best_lbl = labels[best_i]

        short = [l[:22] + "..." if len(l) > 22 else l for l in labels]
        cols = ["#27AE60" if i == best_i else "#95A5A6" for i in range(len(labels))]
        ax.barh(short, probs * 100, color=cols)
        ax.set_xlabel("%")
        ax.set_title(f"{level_name}\n-> \"{best_lbl[:20]}\"", fontsize=9)
        ax.set_xlim(0, 110)
        for j, p in enumerate(probs):
            ax.text(p * 100 + 1, j, f"{p*100:.0f}%", va="center", fontsize=7)

        print(f"\n  {level_name}")
        for lbl, p in sorted(zip(labels, probs), key=lambda x: -x[1]):
            print(f"    {lbl:<40} {p*100:5.1f}%")

    plt.tight_layout()
    out = os.path.join(MEDIA_DIR, "result_hierarchy.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved -> media/result_hierarchy.png")


# -- Demo 3: Image x Label similarity matrix --------------------------------

def run_similarity_matrix(model, preprocess):
    print("\n" + "=" * 58)
    print("BONUS DEMO 3 - Image x Label Similarity Matrix")
    print("=" * 58)

    paths = sorted(
        glob.glob(os.path.join(IMAGES_DIR, "*.jpg")) +
        glob.glob(os.path.join(IMAGES_DIR, "*.jpeg")) +
        glob.glob(os.path.join(IMAGES_DIR, "*.png"))
    )
    if len(paths) < 2:
        print("  Need at least 2 images.")
        return

    labels = ["a dog", "a cat", "a car", "a mountain", "a pizza"]
    all_probs = batch_classify(model, preprocess, paths, labels)

    names = [os.path.splitext(os.path.basename(p))[0] for p in paths]

    fig, ax = plt.subplots(figsize=(len(labels) * 1.6, len(paths) * 1.0 + 1.5))
    im = ax.imshow(all_probs * 100, cmap="YlGn", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.set_yticks(range(len(paths)))
    ax.set_yticklabels(names, fontsize=9)
    ax.set_title("Image x Label Probability Matrix (%)", fontsize=12, fontweight="bold")

    for i in range(len(paths)):
        for j in range(len(labels)):
            val = all_probs[i, j] * 100
            ax.text(j, i, f"{val:.1f}", ha="center", va="center",
                    fontsize=8, color="black" if val < 60 else "white")

    plt.colorbar(im, ax=ax, label="Probability (%)")
    plt.tight_layout()
    out = os.path.join(MEDIA_DIR, "result_similarity_matrix.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved -> media/result_similarity_matrix.png")


# -- Entry point ------------------------------------------------------------

def main():
    print("\n" + "=" * 56)
    print("  CLIP Batch & Bonus Demos - Taller 12.2")
    print("=" * 56 + "\n")

    model, preprocess = load_model()
    run_batch_demo(model, preprocess)
    run_hierarchy_demo(model, preprocess)
    run_similarity_matrix(model, preprocess)

    print("\nBatch demos done! Check the media/ folder.\n")


if __name__ == "__main__":
    main()
