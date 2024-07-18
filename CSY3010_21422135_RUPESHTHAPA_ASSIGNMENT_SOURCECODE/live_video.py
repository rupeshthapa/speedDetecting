import cv2
import time
import threading

import numpy as np
from object_detection_and_tracking import load_yolo_model, detect_and_track_objects
from helper_functions import calculate_distance
from compression import compress_video
from distortion_correction import correct_distortion
from stitching import stitch_videos

def process_live_feed(cameras=[0], speed_limit=5.0, output_path='output.mp4', stitch=False, compress=False, correct_distort=False):
    caps = [cv2.VideoCapture(camera) for camera in cameras]
    if not all([cap.isOpened() for cap in caps]):
        print("Error: Could not open all camera feeds.")
        return

    net, output_layers = load_yolo_model()
    prev_positions = [{} for _ in cameras]
    prev_frame_time = time.time()

    frame_width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(caps[0].get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width * len(caps), frame_height), True)

    while all([cap.isOpened() for cap in caps]):
        frames = []
        for cap in caps:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        if len(frames) != len(caps):
            break

        stitched_frame = np.hstack(frames) if stitch else frames[0]

        for i, frame in enumerate(frames):
            boxes, labels, indexes, current_positions = detect_and_track_objects(frame, net, output_layers, prev_positions[i])
            current_frame_time = time.time()
            frame_time_diff = current_frame_time - prev_frame_time

            if len(indexes) > 0:
                for j in indexes.flatten():
                    x, y, w, h = boxes[j]
                    label = labels[j]
                    color = (0, 255, 0)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                    if j in prev_positions[i]:
                        distance = calculate_distance(prev_positions[i][j], current_positions[j])
                        speed = distance / frame_time_diff  # pixels per second
                        speed_kmh = speed * 3.6  # convert to km/h

                        speed_text = f"Speed: {speed_kmh:.2f} km/h"
                        cv2.putText(frame, speed_text, (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            prev_positions[i] = current_positions
            stitched_frame[:, i * frame_width:(i + 1) * frame_width] = frame

        prev_frame_time = current_frame_time
        cv2.imshow('Live Feed', stitched_frame)
        out.write(stitched_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for cap in caps:
        cap.release()
    out.release()
    cv2.destroyAllWindows()

    if correct_distort:
        corrected_output_path = 'corrected_' + output_path
        correct_distortion(output_path, corrected_output_path)
        output_path = corrected_output_path

    if compress:
        compressed_output_path = 'compressed_' + output_path
        compress_video(output_path, compressed_output_path)

if __name__ == "__main__":
    cameras = [0, 1]  # Example with two cameras
    process_live_feed(cameras=cameras, stitch=True, compress=True, correct_distort=True)
