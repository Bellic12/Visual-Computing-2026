import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import (
    load_image, detect_and_compute, filter_good_matches_ratio,
    draw_matches, save_and_display, IMAGES, ensure_output_dir
)


def main():
    print('=== 3. Cálculo de Homografía ===\n')

    img1 = load_image(IMAGES['box'])
    img2 = load_image(IMAGES['box_in_scene'])

    kp1, des1, _ = detect_and_compute(img1, 'sift')
    kp2, des2, _ = detect_and_compute(img2, 'sift')
    print(f'Keypoints - Box: {len(kp1)}, Scene: {len(kp2)}')

    flann = cv2.FlannBasedMatcher(
        dict(algorithm=1, trees=5),
        dict(checks=50)
    )
    matches = flann.knnMatch(des1, des2, k=2)
    good = filter_good_matches_ratio(matches, 0.75)
    print(f'Good matches (ratio test): {len(good)}')

    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    inliers = mask.sum()
    outliers = len(mask) - inliers

    print(f'\nHomography matrix H (3x3):')
    print(np.array2string(H, precision=4, suppress_small=True))
    print(f'\nRANSAC inliers: {inliers}/{len(mask)} ({100*inliers/len(mask):.1f}%)')
    print(f'RANSAC outliers: {outliers}/{len(mask)} ({100*outliers/len(mask):.1f}%)')

    h, w = img1.shape
    corners_src = np.float32([
        [0, 0], [w, 0], [w, h], [0, h]
    ]).reshape(-1, 1, 2)
    corners_dst = cv2.perspectiveTransform(corners_src, H)
    print(f'\nSource corners projected into scene:')
    for i, (s, d) in enumerate(zip(corners_src, corners_dst)):
        print(f'  Corner {i}: ({s[0][0]:.0f},{s[0][1]:.0f}) -> ({d[0][0]:.1f},{d[0][1]:.1f})')

    mask_bool = mask.ravel().astype(bool)
    inlier_matches = [good[i] for i in range(len(good)) if mask_bool[i]]
    outlier_matches = [good[i] for i in range(len(good)) if not mask_bool[i]]

    print(f'\nInlier matches: {len(inlier_matches)}')
    print(f'Outlier matches: {len(outlier_matches)}')

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    vis_all = draw_matches(img1, kp1, img2, kp2, good, max_draw=100)
    axes[0, 0].imshow(cv2.cvtColor(vis_all, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title(f'All good matches: {len(good)}')
    axes[0, 0].axis('off')

    vis_inliers = draw_matches(img1, kp1, img2, kp2, inlier_matches, max_draw=100)
    axes[0, 1].imshow(cv2.cvtColor(vis_inliers, cv2.COLOR_BGR2RGB))
    axes[0, 1].set_title(f'RANSAC inliers: {len(inlier_matches)} (green)')
    axes[0, 1].axis('off')

    vis_outliers = draw_matches(img1, kp1, img2, kp2, outlier_matches, max_draw=100)
    axes[1, 0].imshow(cv2.cvtColor(vis_outliers, cv2.COLOR_BGR2RGB))
    axes[1, 0].set_title(f'RANSAC outliers: {len(outlier_matches)} (red)')
    axes[1, 0].axis('off')

    img2_color = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
    img_with_box = cv2.polylines(
        img2_color.copy(),
        [np.int32(corners_dst)],
        True, (0, 255, 0), 3, cv2.LINE_AA
    )
    axes[1, 1].imshow(cv2.cvtColor(img_with_box, cv2.COLOR_BGR2RGB))
    axes[1, 1].set_title('Detected box region (from homography)')
    axes[1, 1].axis('off')

    plt.tight_layout()
    save_and_display(fig, '03_homography.png')

    labels = ['Inliers', 'Outliers']
    values = [inliers, outliers]
    colors_labels = ['#4CAF50', '#F44336']

    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.pie(values, labels=labels, autopct='%1.1f%%',
            colors=colors_labels, startangle=90)
    ax1.set_title('RANSAC inlier/outlier ratio')

    ax2.axis('off')
    table_data = [
        ['Total matches', str(len(good))],
        ['RANSAC inliers', str(inliers)],
        ['RANSAC outliers', str(outliers)],
        ['Inlier %', f'{100*inliers/len(mask):.1f}%'],
        ['RANSAC threshold', '5.0'],
    ]
    table = ax2.table(
        cellText=table_data,
        colLabels=['Metric', 'Value'],
        loc='center',
        cellLoc='left'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    ax2.set_title('Homography statistics')

    plt.tight_layout()
    save_and_display(fig2, '03_homography_stats.png')

    print('\nHomography calculation complete.')


if __name__ == '__main__':
    main()
