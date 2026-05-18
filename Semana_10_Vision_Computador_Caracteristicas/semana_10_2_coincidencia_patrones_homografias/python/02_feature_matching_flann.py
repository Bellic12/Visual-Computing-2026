import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from utils import (
    load_image, detect_and_compute, filter_good_matches_ratio,
    draw_matches, save_and_display, IMAGES, ensure_output_dir
)


def main():
    print('=== 2. Feature Matching con FLANN ===\n')

    img1 = load_image(IMAGES['box'])
    img2 = load_image(IMAGES['box_in_scene'])

    kp1_sift, des1_sift, _ = detect_and_compute(img1, 'sift')
    kp2_sift, des2_sift, _ = detect_and_compute(img2, 'sift')

    print(f'SIFT keypoints - Box: {len(kp1_sift)}, Scene: {len(kp2_sift)}')

    FLANN_INDEX_KDTREE = 1
    index_params_sift = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann_sift = cv2.FlannBasedMatcher(index_params_sift, search_params)

    start = time.perf_counter()
    matches_sift = flann_sift.knnMatch(des1_sift, des2_sift, k=2)
    elapsed_sift = time.perf_counter() - start
    print(f'FLANN+SIFT knnMatch: {len(matches_sift)} pairs in {elapsed_sift*1000:.1f} ms')

    good_sift = filter_good_matches_ratio(matches_sift, 0.75)
    print(f'Good matches (ratio 0.75): {len(good_sift)}')

    kp1_orb, des1_orb, _ = detect_and_compute(img1, 'orb')
    kp2_orb, des2_orb, _ = detect_and_compute(img2, 'orb')

    print(f'\nORB keypoints - Box: {len(kp1_orb)}, Scene: {len(kp2_orb)}')

    FLANN_INDEX_LSH = 6
    index_params_orb = dict(
        algorithm=FLANN_INDEX_LSH,
        table_number=12,
        key_size=20,
        multi_probe_level=2
    )

    flann_orb = cv2.FlannBasedMatcher(index_params_orb, search_params)

    des1_orb_32 = des1_orb.astype(np.uint8) if des1_orb.dtype != np.uint8 else des1_orb
    des2_orb_32 = des2_orb.astype(np.uint8) if des2_orb.dtype != np.uint8 else des2_orb

    start = time.perf_counter()
    matches_orb = flann_orb.knnMatch(des1_orb_32, des2_orb_32, k=2)
    elapsed_orb = time.perf_counter() - start
    print(f'FLANN+ORB knnMatch: {len(matches_orb)} pairs in {elapsed_orb*1000:.1f} ms')

    good_orb = filter_good_matches_ratio(matches_orb, 0.75)
    print(f'Good matches (ratio 0.75): {len(good_orb)}')

    bf_sift = cv2.BFMatcher(cv2.NORM_L2)
    start = time.perf_counter()
    bf_matches_sift = bf_sift.knnMatch(des1_sift, des2_sift, k=2)
    bf_elapsed_sift = time.perf_counter() - start

    bf_orb = cv2.BFMatcher(cv2.NORM_HAMMING)
    start = time.perf_counter()
    bf_matches_orb = bf_orb.knnMatch(des1_orb, des2_orb, k=2)
    bf_elapsed_orb = time.perf_counter() - start

    print('\n--- Speed comparison ---')
    print(f'SIFT:  BFMatcher={bf_elapsed_sift*1000:.1f}ms vs FLANN={elapsed_sift*1000:.1f}ms')
    print(f'ORB:   BFMatcher={bf_elapsed_orb*1000:.1f}ms vs FLANN={elapsed_orb*1000:.1f}ms')

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    vis_sift = draw_matches(img1, kp1_sift, img2, kp2_sift, good_sift, max_draw=75)
    axes[0, 0].imshow(cv2.cvtColor(vis_sift, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title(f'FLANN+SIFT: {len(good_sift)} good matches')
    axes[0, 0].axis('off')

    vis_orb = draw_matches(img1, kp1_orb, img2, kp2_orb, good_orb, max_draw=75)
    axes[0, 1].imshow(cv2.cvtColor(vis_orb, cv2.COLOR_BGR2RGB))
    axes[0, 1].set_title(f'FLANN+ORB: {len(good_orb)} good matches')
    axes[0, 1].axis('off')

    methods = ['SIFT BF', 'SIFT FLANN', 'ORB BF', 'ORB FLANN']
    times = [bf_elapsed_sift * 1000, elapsed_sift * 1000,
             bf_elapsed_orb * 1000, elapsed_orb * 1000]
    colors_sift = ['#4CAF50', '#2196F3']
    colors_orb = ['#FF9800', '#F44336']
    bar_colors = colors_sift + colors_orb

    axes[1, 0].bar(methods, times, color=bar_colors)
    axes[1, 0].set_ylabel('Time (ms)')
    axes[1, 0].set_title('Matching speed comparison')
    for i, v in enumerate(times):
        axes[1, 0].text(i, v + 0.5, f'{v:.1f}', ha='center', fontsize=9)

    counts = [
        len(filter_good_matches_ratio(bf_sift.knnMatch(des1_sift, des2_sift, k=2))),
        len(good_sift),
        len(filter_good_matches_ratio(bf_orb.knnMatch(des1_orb, des2_orb, k=2))),
        len(good_orb)
    ]
    axes[1, 1].bar(methods, counts, color=bar_colors)
    axes[1, 1].set_ylabel('Good matches')
    axes[1, 1].set_title('Good matches comparison')
    for i, v in enumerate(counts):
        axes[1, 1].text(i, v + 1, str(v), ha='center', fontsize=9)

    plt.tight_layout()
    save_and_display(fig, '02_flann_comparison.png')

    print('\nFLANN matching complete.')


if __name__ == '__main__':
    main()
