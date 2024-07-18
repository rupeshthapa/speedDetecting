import os
import cv2

def save_annotated_segments(input_path, segments, save_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    for i, (start_frame, end_frame) in enumerate(segments):
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        output_path = os.path.join(save_path, f"segment_{i}.mp4")
        out = cv2.VideoWriter(output_path, fourcc, fps, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))), True)

        for _ in range(start_frame, end_frame + 1):
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        out.release()

    cap.release()

