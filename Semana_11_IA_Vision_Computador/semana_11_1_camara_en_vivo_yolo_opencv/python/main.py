import os
import time
from datetime import datetime

import cv2
from ultralytics import YOLO

CONF_THRESHOLD = 0.5
WINDOW_DET = "YOLO Detection"
WINDOW_FILTER = "Filtered View"


def apply_filter(frame, mode):
    if mode == "gray":
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if mode == "binary":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        return thresh
    if mode == "edges":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return edges
    return frame


def draw_overlay(frame, fps, filter_mode, paused, recording, counts):
    y = 24
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (10, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 255),
        2,
    )
    y += 22
    cv2.putText(
        frame,
        f"Filter: {filter_mode}",
        (10, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )
    y += 22
    total = sum(counts.values()) if counts else 0
    cv2.putText(
        frame,
        f"Objects: {total}",
        (10, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )
    y += 22
    person_count = counts.get("person", 0) if counts else 0
    cv2.putText(
        frame,
        f"Person: {person_count}",
        (10, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )

    if paused:
        cv2.putText(
            frame,
            "PAUSED",
            (10, y + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )
    if recording:
        cv2.putText(
            frame,
            "REC",
            (frame.shape[1] - 70, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )


def main():
    base_dir = os.path.dirname(__file__)
    media_dir = os.path.abspath(os.path.join(base_dir, "..", "media"))
    os.makedirs(media_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: webcam not available.")
        return

    model = YOLO("yolov8n.pt")

    filter_mode = "none"
    auto_person_filter = False
    paused = False
    recording = False
    writer = None

    last_frame = None
    last_results = None
    fps = 0.0

    print("Controls:")
    print("  1: no filter")
    print("  2: gray")
    print("  3: binary")
    print("  4: edges")
    print("  p: pause/resume")
    print("  s: save frame")
    print("  v: start/stop video")
    print("  c: toggle person auto-filter")
    print("  q: quit")

    while True:
        start = time.perf_counter()

        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("Error: frame not captured.")
                break
            last_frame = frame.copy()
        else:
            if last_frame is None:
                continue
            frame = last_frame.copy()

        results = None
        if not paused:
            results = model(frame, conf=CONF_THRESHOLD, verbose=False)[0]
            last_results = results
        else:
            results = last_results

        counts = {}
        person_detected = False

        if results is not None and results.boxes is not None:
            names = results.names
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if conf < CONF_THRESHOLD:
                    continue
                name = names.get(cls_id, str(cls_id))
                counts[name] = counts.get(name, 0) + 1
                if name == "person":
                    person_detected = True

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{name} {conf:.2f}"
                cv2.putText(
                    frame,
                    label,
                    (x1, max(y1 - 6, 16)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2,
                )

        active_filter = filter_mode
        if auto_person_filter and person_detected:
            active_filter = "edges"

        filtered = apply_filter(frame, active_filter)

        elapsed = time.perf_counter() - start
        if elapsed > 0:
            fps = (fps * 0.9) + ((1.0 / elapsed) * 0.1)

        draw_overlay(frame, fps, active_filter, paused, recording, counts)

        if recording and writer is not None:
            writer.write(frame)

        cv2.imshow(WINDOW_DET, frame)
        cv2.imshow(WINDOW_FILTER, filtered)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("p"):
            paused = not paused
        if key == ord("1"):
            filter_mode = "none"
        if key == ord("2"):
            filter_mode = "gray"
        if key == ord("3"):
            filter_mode = "binary"
        if key == ord("4"):
            filter_mode = "edges"
        if key == ord("c"):
            auto_person_filter = not auto_person_filter
        if key == ord("s"):
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(media_dir, f"frame_{stamp}.png")
            cv2.imwrite(path, frame)
            print(f"Saved: {path}")
        if key == ord("v"):
            if not recording:
                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                path = os.path.join(media_dir, f"record_{stamp}.mp4")
                fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                writer = cv2.VideoWriter(
                    path, fourcc, 20.0, (frame.shape[1], frame.shape[0])
                )
                if writer.isOpened():
                    recording = True
                    print(f"Recording: {path}")
                else:
                    writer = None
                    print("Error: video writer not available.")
            else:
                recording = False
                if writer is not None:
                    writer.release()
                    writer = None
                    print("Recording stopped.")

    if writer is not None:
        writer.release()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
