import cv2 as cv
import os
import sys
import math

def compute_fov(focal_length_px, resolution_width):
    # Compute horizontal FoV in degrees
    fov_rad = 2 * math.atan(resolution_width / (2 * focal_length_px))
    return math.degrees(fov_rad)

def run():
    video_folder = os.path.join(os.path.dirname(__file__), '..', 'captured_davis_video')
    video_files = [f for f in os.listdir(video_folder) if f.lower().endswith('.avi')]

    if not video_files:
        print("No AVI files found in the directory.")
        sys.exit(1)

    print("Available video files:")
    for idx, video in enumerate(video_files, start=1):
        print(f"{idx}. {video}")

    choice = input(f"Select a video (1-{len(video_files)}): ")
    try:
        choice = int(choice)
        if choice < 1 or choice > len(video_files):
            raise ValueError
    except ValueError:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    selected_video = video_files[choice - 1]
    video_file = os.path.join(video_folder, selected_video)
    print(f"Playing video: {selected_video}")

    cap = cv.VideoCapture(video_file)
    if not cap.isOpened():
        print("Error: Could not open the video file.")
        return

    fps = cap.get(cv.CAP_PROP_FPS)
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    # === INSERT YOUR FOCAL LENGTH IN PIXELS (fx) HERE ===
    fx = 300.0  # <-- Replace with real value from calibration

    fov = compute_fov(fx, width)
    aspect_ratio = width / height

    print(f"FPS: {fps}")
    print(f"Resolution: {width}x{height}")
    print(f"Aspect Ratio: {aspect_ratio:.2f}")
    print(f"Horizontal FoV (approx): {fov:.2f} degrees")

    cap.release()

if __name__ == "__main__":
    run()
