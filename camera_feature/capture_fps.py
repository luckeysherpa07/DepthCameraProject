import pyzed.sl as sl
import os

def run():
    # Path to the folder containing the videos, go one level up from the current directory
    video_folder = os.path.join(os.path.dirname(__file__), '..', 'captured_videos')

    # List all SVO files in the directory
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.svo2')]

    if not video_files:
        print("No SVO files found in the directory.")
        return

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
        return

    input_file = os.path.join(video_folder, video_files[choice - 1])

    print(f"Playing video: {video_files[choice - 1]}")

    # Set up initialization parameters for playback
    init_parameters = sl.InitParameters()
    init_parameters.set_from_svo_file(input_file)

    # Create a ZED camera object
    zed = sl.Camera()

    # Open the ZED camera or load the SVO file
    err = zed.open(init_parameters)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Failed to open the SVO file.")
        exit(1)

    # Get the FPS of the SVO file
    fps = zed.get_camera_information().camera_configuration.fps
    print(f"FPS of the SVO file: {fps}")
    
    # Get the resolution of the SVO file
    resolution = zed.get_camera_information().camera_configuration.resolution
    print(f"Resolution of the SVO file: {resolution.width}x{resolution.height}")

    # Close the ZED camera after use
    zed.close()

if __name__ == "__main__":
    run()
