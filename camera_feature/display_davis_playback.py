import cv2 as cv
import os
import sys

def run():
    # Path to the folder containing the videos, one level behind the current directory
    video_folder = os.path.join(os.path.dirname(__file__), '..', 'captured_davis_video')

    # List all .avi files in the directory
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.avi')]

    if not video_files:
        print("No AVI files found in the directory.")
        sys.exit(1)

    # Display available video files for the user to select
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

    # Get the selected video file
    selected_video = video_files[choice - 1]
    video_file = os.path.join(video_folder, selected_video)

    # Open the selected video
    cap = cv.VideoCapture(video_file)

    if not cap.isOpened():
        print("Error: Could not open the video file.")
        return

    # Get the video's frame rate (FPS)
    fps = cap.get(cv.CAP_PROP_FPS)

    # Calculate the delay between frames to match the FPS
    frame_delay = int(1000 / fps)  # Delay in milliseconds

    while True:
        # Read the next frame
        ret, frame = cap.read()
        if not ret:
            print("End of video reached. Looping back.")
            cap.set(cv.CAP_PROP_POS_FRAMES, 0)  # Loop back to the start
            continue  # Continue to the next iteration to restart playback

        # Display the frame
        cv.imshow("Playback", frame)

        # Check for key events
        key = cv.waitKey(frame_delay) & 0xFF
        if key == 27:  # ESC key to exit
            break

    cap.release()  # Release the video capture object
    cv.destroyAllWindows()  # Close the OpenCV window

if __name__ == "__main__":
    run()
