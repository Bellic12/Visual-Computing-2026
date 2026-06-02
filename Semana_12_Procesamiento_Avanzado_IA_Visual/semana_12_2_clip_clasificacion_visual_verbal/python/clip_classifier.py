"""
CLIP Image Classifier - Taller Semana 12.2
Classifies images against natural language labels using OpenAI CLIP.
No additional training required.
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
    print("ERROR: Missing dependencies.")
    print("Install CLIP: pip install git+https://github.com/openai/CLIP.git")
    print("Install deps: pip install -r requirements.txt")
    sys.exit(1)

# -- Paths ------------------------------------------------------------------
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR  = os.path.join(BASE_DIR, "..", "media")
IMAGES_DIR = os.path.join(BASE_DIR, "images")

os.makedirs(MEDIA_DIR, exist_ok=True)

# -- Device -----------------------------------------------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# -- Helpers ----------------------------------------------------------------

def find_image(name_no_ext):
    """Return the path of an image regardless of extension (.jpg/.jpeg/.png)."""
    for ext in (".jpg", ".jpeg", ".png"):
        p = os.path.join(IMAGES_DIR, name_no_ext + ext)
        if os.path.exists(p):
            return p
    return None


def load_model():
    print(f"Loading CLIP ViT-B/32 on {DEVICE.upper()}...")
    model, preprocess = clip.load("ViT-B/32", device=DEVICE)
    model.eval()
    print("Model ready.\n")
    return model, preprocess


def classify(model, preprocess, image_path, labels):
    """Return probability array aligned with labels."""
    image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(DEVICE)
    tokens = clip.tokenize(labels).to(DEVICE)
    with torch.no_grad():
        logits, _ = model(image, tokens)
        probs = logits.softmax(dim=-1).cpu().numpy()[0]
    return probs


# -- Visualisation ----------------------------------------------------------

def save_result(image_path, labels, probs, title, filename):
    """Save a side-by-side image + probability bar chart to media/."""
    fig, (ax_img, ax_bar) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(title, fontsize=13, fontweight="bold")

    ax_img.imshow(Image.open(image_path).convert("RGB"))
    ax_img.axis("off")
    best = labels[int(np.argmax(probs))]
    ax_img.set_title(f'Top prediction:\n"{best}"', fontsize=11,
                     color="#27AE60", fontweight="bold")

    idx_best = int(np.argmax(probs))
    colors = ["#27AE60" if i == idx_best else "#2980B9" for i in range(len(labels))]
    bars = ax_bar.barh(labels, probs * 100, color=colors)
    ax_bar.set_xlabel("Probability (%)")
    ax_bar.set_xlim(0, 110)
    ax_bar.set_title("Label probabilities")
    for bar, p in zip(bars, probs):
        ax_bar.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                    f"{p*100:.1f}%", va="center", fontsize=9)

    plt.tight_layout()
    out = os.path.join(MEDIA_DIR, filename)
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved -> media/{filename}")
    return out


# -- Demo 1: basic classification -------------------------------------------

BASIC_TESTS = [
    {
        "image":  "dog",
        "labels": ["a dog", "a cat", "a horse", "a car", "a tree"],
    },
    {
        "image":  "cat",
        "labels": ["a dog", "a cat", "a bird", "a rabbit", "a tiger"],
    },
    {
        "image":  "car",
        "labels": ["a car", "a truck", "a bicycle", "a motorcycle", "a bus"],
    },
    {
        "image":  "mountain",
        "labels": ["a mountain", "a beach", "a forest", "a desert", "a city"],
    },
    {
        "image":  "pizza",
        "labels": ["a pizza", "a burger", "a salad", "a sandwich", "sushi"],
    },
]


def run_basic_demo(model, preprocess):
    print("=" * 58)
    print("DEMO 1 - Basic CLIP Classification")
    print("=" * 58)
    saved = []
    for tc in BASIC_TESTS:
        img_path = find_image(tc["image"])
        if img_path is None:
            print(f"  Skip {tc['image']} (not found in images/)")
            continue

        probs = classify(model, preprocess, img_path, tc["labels"])
        best = tc["labels"][int(np.argmax(probs))]

        print(f"\n[{os.path.basename(img_path)}]  -> best: \"{best}\"")
        for lbl, p in sorted(zip(tc["labels"], probs), key=lambda x: -x[1]):
            print(f"    {lbl:<35} {p*100:5.1f}%")

        fname = f"result_basic_{tc['image']}.png"
        img_name = os.path.basename(img_path)
        out = save_result(img_path, tc["labels"], probs,
                          f"CLIP Classification - {img_name}", fname)
        saved.append(out)
    return saved


# -- Demo 2: simple vs detailed prompts -------------------------------------

def run_prompt_comparison(model, preprocess):
    print("\n" + "=" * 58)
    print("DEMO 2 - Simple vs Detailed Prompts")
    print("=" * 58)

    img_path = find_image("dog")
    if img_path is None:
        print("  Skipping (dog image not found)")
        return None

    simple   = ["dog", "cat", "car", "tree", "bird"]
    detailed = [
        "a fluffy golden Labrador dog looking at the camera",
        "a small tabby cat sitting on a couch",
        "a shiny silver BMW car on a road",
        "a green oak tree in a park",
        "a colorful tropical bird on a branch",
    ]

    p_simple   = classify(model, preprocess, img_path, simple)
    p_detailed = classify(model, preprocess, img_path, detailed)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Simple vs Detailed Prompts - dog", fontsize=13, fontweight="bold")

    axes[0].imshow(Image.open(img_path).convert("RGB"))
    axes[0].axis("off")
    axes[0].set_title("Input Image")

    for ax, labels, probs, title, color in [
        (axes[1], simple,   p_simple,   "Simple labels",   "#2980B9"),
        (axes[2], detailed, p_detailed, "Detailed labels",  "#8E44AD"),
    ]:
        best_i = int(np.argmax(probs))
        cols = ["#27AE60" if i == best_i else color for i in range(len(labels))]
        short = [l[:30] + "..." if len(l) > 30 else l for l in labels]
        ax.barh(short, probs * 100, color=cols)
        ax.set_xlabel("Probability (%)")
        ax.set_title(title)
        ax.set_xlim(0, 110)
        for j, p in enumerate(probs):
            ax.text(p * 100 + 1, j, f"{p*100:.1f}%", va="center", fontsize=8)

    plt.tight_layout()
    out = os.path.join(MEDIA_DIR, "result_prompt_comparison.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print("  Saved -> media/result_prompt_comparison.png")
    return out


# -- Demo 3: ambiguous / subjective prompts ---------------------------------

AMBIGUOUS_TESTS = [
    {
        "image":  "dog",
        "labels": ["something happy", "something sad", "something cute",
                   "something scary", "something boring"],
        "title":  "Subjective attributes - dog",
    },
    {
        "image":  "pizza",
        "labels": ["healthy food", "junk food", "gourmet cuisine",
                   "comfort food", "disgusting food"],
        "title":  "Subjective food labels - pizza",
    },
    {
        "image":  "mountain",
        "labels": ["a dangerous place", "a peaceful place", "a magical place",
                   "a cold place", "a crowded place"],
        "title":  "Subjective place labels - mountain",
    },
]


def run_ambiguous_demo(model, preprocess):
    print("\n" + "=" * 58)
    print("DEMO 3 - Ambiguous & Subjective Prompts")
    print("=" * 58)
    saved = []
    for tc in AMBIGUOUS_TESTS:
        img_path = find_image(tc["image"])
        if img_path is None:
            continue

        probs = classify(model, preprocess, img_path, tc["labels"])
        best = tc["labels"][int(np.argmax(probs))]
        print(f"\n[{tc['title']}]  -> best: \"{best}\"")
        for lbl, p in sorted(zip(tc["labels"], probs), key=lambda x: -x[1]):
            print(f"    {lbl:<40} {p*100:5.1f}%")

        fname = f"result_ambiguous_{tc['image']}.png"
        out = save_result(img_path, tc["labels"], probs, tc["title"], fname)
        saved.append(out)
    return saved


# -- Animated GIF from all saved PNGs ---------------------------------------

def create_summary_gif():
    frames_paths = sorted(glob.glob(os.path.join(MEDIA_DIR, "result_*.png")))
    if not frames_paths:
        print("  No result PNGs found; skipping GIF creation.")
        return

    TARGET = (900, 375)
    frames = [Image.open(p).convert("RGB").resize(TARGET, Image.LANCZOS)
              for p in frames_paths]

    gif_path = os.path.join(MEDIA_DIR, "clip_demo.gif")
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=2500,
        loop=0,
    )
    print(f"  Animated GIF -> media/clip_demo.gif  ({len(frames)} frames)")


# -- Entry point ------------------------------------------------------------

def main():
    print("\n" + "=" * 56)
    print("   CLIP Visual-Verbal Image Classifier - Taller 12.2")
    print("=" * 56 + "\n")

    model, preprocess = load_model()

    run_basic_demo(model, preprocess)
    run_prompt_comparison(model, preprocess)
    run_ambiguous_demo(model, preprocess)

    print("\nCreating animated GIF summary...")
    create_summary_gif()

    print("\nDone! All results are in the media/ folder.\n")


if __name__ == "__main__":
    main()
