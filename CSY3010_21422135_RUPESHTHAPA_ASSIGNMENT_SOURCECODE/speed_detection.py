import cv2
import numpy as np
from object_detection_and_tracking import load_yolo_model, detect_and_track_objects
from helper_functions import calculate_distance
from categorize import categorize_movements

def detect_speeding(video_path, speed_limit=5.0):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return [], {}, {}

    net, output_layers = load_yolo_model()
    prev_positions = {}
    segments = []
    categorized_movements = {"human": [], "bike": [], "vehicle": []}
    speeds = {}

    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_time = 1.0 / frame_rate
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    segment_start = None

    heatmap = None

    for frame_num in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break

        if heatmap is None:
            heatmap = np.zeros_like(frame[:, :, 0])

        boxes, labels, indexes, current_positions = detect_and_track_objects(frame, net, output_layers, prev_positions)

        if len(indexes) > 0:
            for i in indexes.flatten():
                if i in prev_positions:
                    distance = calculate_distance(prev_positions[i], current_positions[i])
                    speed = distance / frame_time  # pixels per second
                    speeds[i] = speed  # Store the speed of each object

                    if speed > speed_limit:
                        if segment_start is None:
                            segment_start = frame_num

                        color = (0, 0, 255)  # Red for speeding
                    else:
                        color = (0, 255, 0)  # Green for normal

                    x, y, w, h = boxes[i]
                    label = labels[i]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"{label} {speed:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    categorized_movements = categorize_movements(labels, boxes, indexes)
                else:
                    color = (0, 255, 0)  # Green for normal
                    x, y, w, h = boxes[i]
                    label = labels[i]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # Update heatmap
                heatmap[y:y + h, x:x + w] += 1

        else:
            if segment_start is not None:
                segments.append((segment_start, frame_num - 1))
                segment_start = None

        prev_positions = current_positions

        # Normalize and colorize heatmap
        normalized_heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_color = cv2.applyColorMap(np.uint8(normalized_heatmap), cv2.COLORMAP_JET)

        # Blend heatmap with frame
        blended_frame = cv2.addWeighted(frame, 0.7, heatmap_color, 0.3, 0)

        cv2.imshow('Frame with Heatmap', blended_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if segment_start is not None:
        segments.append((segment_start, frame_count - 1))

    cap.release()
    cv2.destroyAllWindows()

    return segments, categorized_movements, speeds
