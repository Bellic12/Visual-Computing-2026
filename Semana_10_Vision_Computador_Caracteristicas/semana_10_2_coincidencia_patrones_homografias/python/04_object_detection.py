import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import (
    load_image, load_image_rgb, detect_and_compute,
    filter_good_matches_ratio, save_and_display, IMAGES, ensure_output_dir
)


def main():
    print('=== 4. Detección de Objetos ===\n')

    template = load_image(IMAGES['box'])
    scene = load_image(IMAGES['box_in_scene'])
    template_rgb = load_image_rgb(IMAGES['box'])
    scene_rgb = load_image_rgb(IMAGES['box_in_scene'])

    print(f'Template (object): {template.shape[::-1]}')
    print(f'Scene: {scene.shape[::-1]}')

    kp_t, des_t, _ = detect_and_compute(template, 'sift')
    kp_s, des_s, _ = detect_and_compute(scene, 'sift')
    print(f'Keypoints - Template: {len(kp_t)}, Scene: {len(kp_s)}')

    flann = cv2.FlannBasedMatcher(
        dict(algorithm=1, trees=5),
        dict(checks=50)
    )
    matches = flann.knnMatch(des_t, des_s, k=2)
    good = filter_good_matches_ratio(matches, 0.75)
    print(f'Good matches: {len(good)}')

    MIN_MATCHES = 10
    object_detected = len(good) >= MIN_MATCHES

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    axes[0, 0].imshow(template_rgb, cmap='gray')
    axes[0, 0].set_title(f'Object to detect (template)\n{template.shape[1]}x{template.shape[0]}')
    axes[0, 0].axis('off')

    scene_with_detection = scene_rgb.copy()

    if object_detected:
        src_pts = np.float32([kp_t[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_s[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        inliers = mask.sum()

        h, w = template.shape
        corners = np.float32([
            [0, 0], [w, 0], [w, h], [0, h]
        ]).reshape(-1, 1, 2)
        projected = cv2.perspectiveTransform(corners, H)

        scene_with_detection = cv2.cvtColor(scene, cv2.COLOR_GRAY2BGR)
        scene_with_detection = cv2.polylines(
            scene_with_detection,
            [np.int32(projected)],
            True, (0, 255, 0), 3, cv2.LINE_AA
        )

        cv2.putText(
            scene_with_detection,
            f'Object detected ({inliers} inliers)',
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (0, 255, 0), 2, cv2.LINE_AA
        )

        axes[1, 0].imshow(cv2.cvtColor(scene_with_detection, cv2.COLOR_BGR2RGB))
        axes[1, 0].set_title(f'Object detected! Bounding box drawn')
        axes[1, 0].axis('off')

        mask_bool = mask.ravel().astype(bool)
        inlier_matches = [good[i] for i in range(len(good)) if mask_bool[i]]
        outlier_matches = [good[i] for i in range(len(good)) if not mask_bool[i]]

        from utils import draw_matches
        vis = draw_matches(template, kp_t, scene, kp_s, inlier_matches, max_draw=75)
        axes[1, 1].imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
        axes[1, 1].set_title(f'Geometric verification: {len(inlier_matches)} inliers')
        axes[1, 1].axis('off')

        print(f'\nObject DETECTED with {inliers} geometric inliers!')
        print(f'Homography matrix:')
        print(np.array2string(H, precision=3, suppress_small=True))
    else:
        axes[1, 0].imshow(scene_rgb)
        axes[1, 0].set_title('Object NOT detected (too few matches)')
        axes[1, 0].axis('off')
        axes[1, 1].axis('off')
        print('\nObject NOT detected - insufficient matches')

    axes[0, 1].imshow(scene_rgb)
    axes[0, 1].set_title('Original scene image')
    axes[0, 1].axis('off')

    plt.tight_layout()
    save_and_display(fig, '04_object_detection.png')

    print('\nObject detection complete.')


if __name__ == '__main__':
    main()
