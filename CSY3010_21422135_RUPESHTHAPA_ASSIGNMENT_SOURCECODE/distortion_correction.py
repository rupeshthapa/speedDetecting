import cv2
import numpy as np

def correct_distortion(input_path, output_path):
    # Load camera calibration data (for example purposes, usually these values are obtained through calibration)
    K = np.array([[1.15422732e+03, 0.00000000e+00, 6.71627794e+02],
                  [0.00000000e+00, 1.14818221e+03, 3.86046312e+02],
                  [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    dist_coeffs = np.array([[-2.42565104e-01, -4.77893070e-02, -1.31388084e-03, -8.79107779e-05, 2.20573263e-02]])

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height), True)
    if not out.isOpened():
        print("Error: Could not open video writer.")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(K, dist_coeffs, (w, h), 1, (w, h))
        undistorted_frame = cv2.undistort(frame, K, dist_coeffs, None, new_camera_matrix)

        out.write(undistorted_frame)

    cap.release()
    out.release()
