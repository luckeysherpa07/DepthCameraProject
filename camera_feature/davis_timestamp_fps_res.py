import cv2 as cv
import os
import sys

def run():
    # Path to the folder containing the videos, go one level up from the current directory
    video_folder = os.path.join(os.path.dirname(__file__), '..', 'captured_davis_video')
    video_files = [f for f in os.listdir(video_folder) if f.lower().endswith('.avi')]

    if not video_files:
        print("No AVI files found in the directory.")
        sys.exit(1)

    # Display available video files
    print("Available video files:")
    for idx, video in enumerate(video_files, start=1):
        print(f"{idx}. {video}")

    # Ask the user to select a video
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

    # Open the video file using OpenCV
    cap = cv.VideoCapture(video_file)
    if not cap.isOpened():
        print("Error: Could not open the video file.")
        return

    # Get video properties
    fps = cap.get(cv.CAP_PROP_FPS)
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))

    # Display video information
    print(f"FPS: {fps}")
    print(f"Resolution: {width}x{height}")

    # Assuming the starting timestamp for the other device (e.g., depth camera)
    # Start timestamp from the other device (in nanoseconds from epoch)
    depth_camera_start_ns = 1745407877796142228  # Example timestamp (nanoseconds from epoch)

    # Calculate the ending timestamp (in seconds)
    end_timestamp_sec = total_frames / fps

    # Convert event camera timestamp (in seconds) to nanoseconds from epoch for synchronization
    # Example: If event camera timestamp is 1.5 seconds, convert to nanoseconds:
    event_relative_sec = 1.5  # Example event timestamp in seconds
    event_absolute_ns = depth_camera_start_ns + int(event_relative_sec * 1e9)

    print(f"Starting timestamp (from other device in nanoseconds): {depth_camera_start_ns}")
    print(f"Ending timestamp (in seconds): {end_timestamp_sec:.6f}")
    print(f"Event timestamp (converted to nanoseconds from epoch): {event_absolute_ns}")

    cap.release()

if __name__ == "__main__":
    run()
