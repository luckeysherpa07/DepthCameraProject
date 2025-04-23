import cv2
import os

def run():
    # Path to the folder containing the DAVIS video
    video_folder = os.path.join(os.path.dirname(__file__), '..', 'captured_davis_video')

    # List all AVI files
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.avi')]

    if not video_files:
        print("No AVI files found in the directory.")
        return

    # Display available video files
    print("Available video files:")
    for idx, video in enumerate(video_files, start=1):
        print(f"{idx}. {video}")

    # Ask user to choose
    choice = input(f"Select a video (1-{len(video_files)}): ")

    try:
        choice = int(choice)
        if choice < 1 or choice > len(video_files):
            raise ValueError
    except ValueError:
        print("Invalid choice. Exiting.")
        return

    video_path = os.path.join(video_folder, video_files[choice - 1])
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Failed to open the video.")
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    duration_sec = frame_count / fps if fps else 0

    print(f"FPS: {fps}")
    print(f"Resolution: {width}x{height}")
    print(f"Frame Count: {frame_count}")
    print(f"Duration (s): {duration_sec:.2f}")

    # Timestamps in nanoseconds
    first_frame_timestamp_ns = 0
    last_frame_timestamp_ns = int(duration_sec * 1e9)

    print(f"Start timestamp: {first_frame_timestamp_ns} ns")
    print(f"End timestamp: {last_frame_timestamp_ns} ns")

    cap.release()

if __name__ == "__main__":
    run()
