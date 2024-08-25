import cv2
import numpy as np

def stitch_videos(video_paths, output_path):
    caps = [cv2.VideoCapture(video_path) for video_path in video_paths]
    if not all([cap.isOpened() for cap in caps]):
        raise Exception("Error: Could not open all videos.")

    frame_width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(caps[0].get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height), True)
    if not out.isOpened():
        raise Exception("Error: Could not open video writer.")

    while True:
        frames = []
        for cap in caps:
            ret, frame = cap.read()
            if not ret:
                break
            resized_frame = cv2.resize(frame, (frame_width, frame_height))
            frames.append(resized_frame)

        if len(frames) != len(caps):
            break

        stitched_frame = np.mean(frames, axis=0).astype(np.uint8)
        out.write(stitched_frame)

    for cap in caps:
        cap.release()
    out.release()
