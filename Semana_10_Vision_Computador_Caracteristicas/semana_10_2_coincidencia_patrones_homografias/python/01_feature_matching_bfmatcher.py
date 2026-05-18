import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import (
    load_image, load_image_rgb, detect_and_compute,
    draw_matches, save_and_display, IMAGES, ensure_output_dir
)


def main():
    print('=== 1. Feature Matching con BFMatcher ===\n')

    img1 = load_image(IMAGES['box'])
    img2 = load_image(IMAGES['box_in_scene'])
    img1_rgb = load_image_rgb(IMAGES['box'])
    img2_rgb = load_image_rgb(IMAGES['box_in_scene'])

    print(f'Box image: {img1.shape[::-1]}')
    print(f'Scene image: {img2.shape[::-1]}')

    for method in ['sift', 'orb']:
        print(f'\n--- Using {method.upper()} ---')
        kp1, des1, _ = detect_and_compute(img1, method)
        kp2, des2, _ = detect_and_compute(img2, method)
        print(f'  Keypoints in box: {len(kp1)}')
        print(f'  Keypoints in scene: {len(kp2)}')

        bf = cv2.BFMatcher(cv2.NORM_L2 if method == 'sift' else cv2.NORM_HAMMING)

        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        print(f'  Total matches (BF.match): {len(matches)}')

        fig, axes = plt.subplots(2, 2, figsize=(16, 10))

        axes[0, 0].imshow(img1_rgb, cmap='gray')
        axes[0, 0].set_title(f'Box Image - {len(kp1)} keypoints')
        axes[0, 0].axis('off')

        axes[0, 1].imshow(img2_rgb, cmap='gray')
        axes[0, 1].set_title(f'Scene Image - {len(kp2)} keypoints')
        axes[0, 1].axis('off')

        vis_all = draw_matches(img1, kp1, img2, kp2, matches, max_draw=50)
        axes[1, 0].imshow(cv2.cvtColor(vis_all, cv2.COLOR_BGR2RGB))
        axes[1, 0].set_title(f'Top 50 BF.matches (sorted by distance)')
        axes[1, 0].axis('off')

        distances = [m.distance for m in matches]
        axes[1, 1].hist(distances, bins=30, color='steelblue', edgecolor='white')
        axes[1, 1].set_title(f'Distance distribution ({len(matches)} matches)')
        axes[1, 1].set_xlabel('Distance')
        axes[1, 1].set_ylabel('Count')

        plt.tight_layout()
        save_and_display(fig, f'01_bfmatcher_{method}.png')

        bf_knn = cv2.BFMatcher(cv2.NORM_L2 if method == 'sift' else cv2.NORM_HAMMING)
        knn_matches = bf_knn.knnMatch(des1, des2, k=2)
        print(f'  KNN match pairs: {len(knn_matches)}')

        good = []
        for m, n in knn_matches:
            if m.distance < 0.75 * n.distance:
                good.append(m)
        print(f'  Good matches (ratio test 0.75): {len(good)}')

        fig2, ax = plt.subplots(1, 1, figsize=(14, 6))
        vis_good = draw_matches(img1, kp1, img2, kp2, good, max_draw=100)
        ax.imshow(cv2.cvtColor(vis_good, cv2.COLOR_BGR2RGB))
        ax.set_title(f'{method.upper()} BFMatcher kNN - {len(good)} good matches')
        ax.axis('off')
        plt.tight_layout()
        save_and_display(fig2, f'01_bfmatcher_knn_{method}.png')

    print('\nBFMatcher complete.')


if __name__ == '__main__':
    main()
