import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from utils import (
    load_image, detect_and_compute, filter_good_matches_ratio,
    save_and_display, IMAGES, MEDIA_DIR, ensure_output_dir
)


def load_images_from_paths(paths, flags=cv2.IMREAD_COLOR):
    images = []
    for p in paths:
        img = cv2.imread(str(p), flags)
        if img is None:
            raise FileNotFoundError(f'Could not load: {p}')
        images.append(img)
    return images


def warp_and_blend(img1, img2, H):
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    corners1 = np.float32([
        [0, 0], [0, h1], [w1, h1], [w1, 0]
    ]).reshape(-1, 1, 2)
    corners2 = np.float32([
        [0, 0], [0, h2], [w2, h2], [w2, 0]
    ]).reshape(-1, 1, 2)

    corners2_in_1 = cv2.perspectiveTransform(corners2, H)
    all_corners = np.concatenate((corners1, corners2_in_1), axis=0)
    all_corners_int = all_corners.reshape(-1, 2).astype(np.int32)

    x_min, y_min = all_corners_int.min(axis=0)
    x_max, y_max = all_corners_int.max(axis=0)

    x_min = min(x_min, 0)
    y_min = min(y_min, 0)

    out_w = x_max - x_min
    out_h = y_max - y_min

    translation = np.array([
        [1, 0, -x_min],
        [0, 1, -y_min],
        [0, 0, 1]
    ], dtype=np.float64)

    img1_warped = cv2.warpPerspective(
        img1, translation, (out_w, out_h),
        flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
    )

    H_adjusted = translation @ H
    img2_warped = cv2.warpPerspective(
        img2, H_adjusted, (out_w, out_h),
        flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
    )

    mask1 = (img1_warped > 0).astype(np.float32)
    mask2 = (img2_warped > 0).astype(np.float32)
    overlap = cv2.bitwise_and(
        (mask1[:, :, 0] > 0).astype(np.uint8),
        (mask2[:, :, 0] > 0).astype(np.uint8)
    )

    if overlap.sum() > 0:
        ys, xs = np.where(overlap > 0)
        x_start, x_end = xs.min(), xs.max()

        blend = np.zeros_like(img1_warped, dtype=np.float32)
        for c in range(3):
            for y in range(out_h):
                for x in range(out_w):
                    if overlap[y, x]:
                        alpha = (x - x_start) / max(x_end - x_start, 1)
                        alpha = np.clip(alpha, 0.0, 1.0)
                        blend[y, x, c] = (1 - alpha) * img1_warped[y, x, c] + alpha * img2_warped[y, x, c]
                    elif mask1[y, x, 0] > 0:
                        blend[y, x, c] = img1_warped[y, x, c]
                    elif mask2[y, x, 0] > 0:
                        blend[y, x, c] = img2_warped[y, x, c]

        stitched = blend.astype(np.uint8)
    else:
        stitched = cv2.add(img1_warped, img2_warped)

    return stitched


def main():
    print('=== 5. Image Stitching (Panorama) ===\n')

    calib_dir = Path(IMAGES['box']).parent.parent / 'unity' / \
        'Assets' / 'OpenCVForUnity' / 'StreamingAssets' / \
        'OpenCVForUnityExamples' / 'objdetect' / 'calibration_images'

    calib_dir_resolved = calib_dir.resolve()
    if not calib_dir_resolved.exists():
        print(f'Calibration images not found at: {calib_dir_resolved}')
        print('Using alternative approach with bike image...')
        from utils import load_image_rgb
        bike = load_image_rgb(IMAGES['bike'])
        h, w = bike.shape[:2]
        mid = w // 2
        overlap = w // 5
        left_img = bike[:, :mid + overlap]
        right_img = bike[:, mid - overlap:]
        images_rgb = [left_img, right_img]
        image_names = ['bike_left', 'bike_right']
    else:
        calib_files = sorted(calib_dir_resolved.glob('left*.jpg'))
        if len(calib_files) >= 3:
            selected = [calib_files[3], calib_files[5], calib_files[7]]
        elif len(calib_files) >= 2:
            selected = [calib_files[0], calib_files[1]]
        else:
            selected = list(calib_files)
        print(f'Using calibration images: {[p.name for p in selected]}')
        images_rgb = load_images_from_paths(selected, cv2.IMREAD_COLOR)
        images_rgb = [cv2.cvtColor(img, cv2.COLOR_BGR2RGB) for img in images_rgb]
        image_names = [p.stem for p in selected]

    print(f'Number of images: {len(images_rgb)}')
    for i, img in enumerate(images_rgb):
        print(f'  Image {i+1}: {img.shape[1]}x{img.shape[0]}')

    fig, axes = plt.subplots(1, len(images_rgb), figsize=(6 * len(images_rgb), 5))
    if len(images_rgb) == 1:
        axes = [axes]
    for i, (ax, img, name) in enumerate(zip(axes, images_rgb, image_names)):
        ax.imshow(img)
        ax.set_title(f'{name}\n{img.shape[1]}x{img.shape[0]}')
        ax.axis('off')
    plt.tight_layout()
    save_and_display(fig, '05_panorama_input_images.png')

    gray_images = [cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) for img in images_rgb]

    print('\nComputing pairwise homographies...')
    current_panorama = images_rgb[0]

    for i in range(1, len(images_rgb)):
        print(f'\n  Stitching image {i+1} ({image_names[i]}) into panorama...')
        gray_current = cv2.cvtColor(current_panorama, cv2.COLOR_RGB2GRAY)
        gray_next = gray_images[i]

        kp1, des1, _ = detect_and_compute(gray_current, 'sift')
        kp2, des2, _ = detect_and_compute(gray_next, 'sift')
        print(f'    Keypoints: panorama={len(kp1)}, img{i+1}={len(kp2)}')

        flann = cv2.FlannBasedMatcher(
            dict(algorithm=1, trees=5),
            dict(checks=50)
        )
        matches = flann.knnMatch(des1, des2, k=2)
        good = filter_good_matches_ratio(matches, 0.7)
        print(f'    Good matches: {len(good)}')

        if len(good) < 10:
            print(f'    WARNING: Too few matches ({len(good)}), skipping this image')
            continue

        src_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        inliers = mask.sum() if mask is not None else 0
        print(f'    RANSAC inliers: {inliers}/{len(good)}')

        current_panorama = warp_and_blend(current_panorama, images_rgb[i], H)
        print(f'    Panorama size: {current_panorama.shape[1]}x{current_panorama.shape[0]}')

    fig2, ax = plt.subplots(1, 1, figsize=(16, 8))
    ax.imshow(current_panorama)
    ax.set_title(f'Final Panorama ({current_panorama.shape[1]}x{current_panorama.shape[0]})')
    ax.axis('off')
    plt.tight_layout()
    save_and_display(fig2, '05_panorama_result.png')

    print(f'\nPanorama stitching complete.')


if __name__ == '__main__':
    main()
