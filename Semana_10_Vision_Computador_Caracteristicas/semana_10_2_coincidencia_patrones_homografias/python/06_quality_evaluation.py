import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from utils import (
    load_image, detect_and_compute, filter_good_matches_ratio,
    save_and_display, IMAGES, ensure_output_dir
)


def evaluate_matching(img1, img2, method='sift', matcher_type='flann'):
    kp1, des1, _ = detect_and_compute(img1, method)
    kp2, des2, _ = detect_and_compute(img2, method)

    if matcher_type == 'flann':
        if method == 'sift':
            index_params = dict(algorithm=1, trees=5)
        else:
            index_params = dict(
                algorithm=6, table_number=12,
                key_size=20, multi_probe_level=2
            )
        matcher = cv2.FlannBasedMatcher(index_params, dict(checks=50))
    else:
        norm = cv2.NORM_L2 if method == 'sift' else cv2.NORM_HAMMING
        matcher = cv2.BFMatcher(norm)

    start = time.perf_counter()
    matches = matcher.knnMatch(des1, des2, k=2)
    match_time = time.perf_counter() - start

    good = filter_good_matches_ratio(matches, 0.75)

    if len(good) >= 4:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        if mask is not None:
            inlier_ratio = mask.sum() / len(mask)
            inliers = int(mask.sum())
        else:
            inlier_ratio = 0
            inliers = 0
    else:
        inlier_ratio = 0
        inliers = 0

    return {
        'method': method,
        'matcher': matcher_type,
        'keypoints1': len(kp1),
        'keypoints2': len(kp2),
        'total_matches': len(matches),
        'good_matches': len(good),
        'ransac_inliers': inliers,
        'inlier_ratio': inlier_ratio,
        'match_time_ms': match_time * 1000,
    }


def main():
    print('=== 6. Evaluación de Calidad ===\n')

    img1 = load_image(IMAGES['box'])
    img2 = load_image(IMAGES['box_in_scene'])

    configs = [
        ('sift', 'flann'),
        ('sift', 'bf'),
        ('orb', 'flann'),
        ('orb', 'bf'),
    ]

    results = []
    for method, matcher in configs:
        print(f'Evaluating {method.upper()} + {matcher.upper()}...')
        r = evaluate_matching(img1, img2, method, matcher)
        results.append(r)
        print(f'  Keypoints: {r["keypoints1"]} / {r["keypoints2"]}')
        print(f'  Total matches: {r["total_matches"]}')
        print(f'  Good matches (ratio test): {r["good_matches"]}')
        print(f'  RANSAC inliers: {r["ransac_inliers"]} ({r["inlier_ratio"]:.1%})')
        print(f'  Match time: {r["match_time_ms"]:.2f} ms')
        print()

    for r in results:
        r['inlier_ratio'] = r['inlier_ratio'] if r['inlier_ratio'] > 0 else 0.001

    labels = [f'{r["method"].upper()}\n{r["matcher"].upper()}' for r in results]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    metrics_good = [r['good_matches'] for r in results]
    bars0 = axes[0, 0].bar(labels, metrics_good, color=['#2196F3', '#4CAF50', '#FF9800', '#F44336'])
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].set_title('Good matches (after ratio test)')
    for bar, v in zip(bars0, metrics_good):
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        str(v), ha='center', fontsize=10)

    metrics_inliers = [r['ransac_inliers'] for r in results]
    bars1 = axes[0, 1].bar(labels, metrics_inliers, color=['#2196F3', '#4CAF50', '#FF9800', '#F44336'])
    axes[0, 1].set_ylabel('Count')
    axes[0, 1].set_title('RANSAC inliers')
    for bar, v in zip(bars1, metrics_inliers):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        str(v), ha='center', fontsize=10)

    metrics_time = [r['match_time_ms'] for r in results]
    bars2 = axes[1, 0].bar(labels, metrics_time, color=['#2196F3', '#4CAF50', '#FF9800', '#F44336'])
    axes[1, 0].set_ylabel('Time (ms)')
    axes[1, 0].set_title('Matching time (lower is better)')
    for bar, v in zip(bars2, metrics_time):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{v:.1f}', ha='center', fontsize=9)

    metrics_ratio = [r['inlier_ratio'] * 100 for r in results]
    bars3 = axes[1, 1].bar(labels, metrics_ratio, color=['#2196F3', '#4CAF50', '#FF9800', '#F44336'])
    axes[1, 1].set_ylabel('Inlier ratio (%)')
    axes[1, 1].set_title('RANSAC inlier percentage')
    for bar, v in zip(bars3, metrics_ratio):
        axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{v:.1f}%', ha='center', fontsize=9)

    plt.tight_layout()
    save_and_display(fig, '06_quality_evaluation.png')

    fig2, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    col_labels = ['Method', 'Matcher', 'KPs (img1/img2)', 'Total matches',
                   'Good matches', 'Inliers', 'Inlier %', 'Time (ms)']
    cell_data = []
    for r in results:
        cell_data.append([
            r['method'].upper(),
            r['matcher'].upper(),
            f'{r["keypoints1"]}/{r["keypoints2"]}',
            str(r['total_matches']),
            str(r['good_matches']),
            str(r['ransac_inliers']),
            f'{r["inlier_ratio"]:.1%}',
            f'{r["match_time_ms"]:.2f}'
        ])
    table = ax.table(
        cellText=cell_data,
        colLabels=col_labels,
        loc='center',
        cellLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.6)
    ax.set_title('Quality Metrics Summary', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    save_and_display(fig2, '06_quality_summary_table.png')

    print('\nBest configuration:')
    best = max(results, key=lambda r: r['inlier_ratio'])
    print(f'  {best["method"].upper()} + {best["matcher"].upper()}: '
          f'{best["ransac_inliers"]} inliers ({best["inlier_ratio"]:.1%})')

    fastest = min(results, key=lambda r: r['match_time_ms'])
    print(f'  Fastest: {fastest["method"].upper()} + {fastest["matcher"].upper()}: '
          f'{fastest["match_time_ms"]:.2f} ms')

    print('\nQuality evaluation complete.')


if __name__ == '__main__':
    main()
