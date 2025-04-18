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

    # Get FPS and resolution of the SVO file
    fps = zed.get_camera_information().camera_configuration.fps
    resolution = zed.get_camera_information().camera_configuration.resolution
    print(f"FPS: {fps}")
    print(f"Resolution: {resolution.width}x{resolution.height}")

    # Variables to store timestamps
    first_frame_timestamp = None
    last_frame_timestamp = None

    # Grab the first frame (to get the starting timestamp)
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        first_frame_timestamp = zed.get_timestamp(sl.TIME_REFERENCE.CURRENT).get_nanoseconds()
        print(f"Starting timestamp in nanosecond: {first_frame_timestamp}")

    # Loop through the SVO file to get the last frame's timestamp
    while zed.grab() == sl.ERROR_CODE.SUCCESS:
        last_frame_timestamp = zed.get_timestamp(sl.TIME_REFERENCE.CURRENT).get_nanoseconds()

    # Close the ZED camera after use
    zed.close()

    # Print the last frame's timestamp
    if last_frame_timestamp:
        print(f"Ending timestamp in nanosecond: {last_frame_timestamp}")

if __name__ == "__main__":
    run()
