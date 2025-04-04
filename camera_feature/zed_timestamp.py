import pyzed.sl as sl
import os

# Function to convert nanoseconds to hours, minutes, and seconds
# def convert_to_hms(timestamp_ns):
#     timestamp_s = timestamp_ns / 1e9  # Convert nanoseconds to seconds
#     hours = int(timestamp_s // 3600)
#     minutes = int((timestamp_s % 3600) // 60)
#     seconds = int(timestamp_s % 60)
#     return hours, minutes, seconds

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

    init_parameters = sl.InitParameters()
    init_parameters.set_from_svo_file(input_file)

    # Initialize the ZED camera for playback
    zed = sl.Camera()
    if zed.open(init_parameters) != sl.ERROR_CODE.SUCCESS:
        print("Failed to open SVO file.")
        return

    # Variables to store timestamps
    first_frame_timestamp = None
    last_frame_timestamp = None

    # Grab the first frame (to get the starting timestamp)
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        first_frame_timestamp = zed.get_timestamp(sl.TIME_REFERENCE.CURRENT).get_nanoseconds()
        # first_hms = convert_to_hms(first_frame_timestamp)
        # print(f"Starting timestamp: {first_hms[0]:02}:{first_hms[1]:02}:{first_hms[2]:02}")
        print(f"Starting timestamp in nanosecond: {first_frame_timestamp}")

    # Loop through the SVO file to get the last frame's timestamp
    while zed.grab() == sl.ERROR_CODE.SUCCESS:
        last_frame_timestamp = zed.get_timestamp(sl.TIME_REFERENCE.CURRENT).get_nanoseconds()

    # Close the ZED camera
    zed.close()

    # Print the last frame's timestamp
    if last_frame_timestamp:
        # last_hms = convert_to_hms(last_frame_timestamp)
        # print(f"Ending timestamp: {last_hms[0]:02}:{last_hms[1]:02}:{last_hms[2]:02}")
        print(f"Ending timestamp in nanosecond: {last_frame_timestamp}")

if __name__ == "__main__":
    run()
