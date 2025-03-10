import pyzed.sl as sl
import time
import os

def get_next_filename(directory, base_filename):
    # Generate the next available file name by incrementing the number
    i = 1
    while os.path.exists(os.path.join(directory, f"{base_filename}{i}.svo")):
        i += 1
    return os.path.join(directory, f"{base_filename}{i}.svo")

def run():
    # Create a ZED camera object
    zed = sl.Camera()

    # Define the base path and filename
    directory = os.path.dirname(os.path.abspath(__file__))
    base_filename = "output"

    # Get the next available filename
    output_path = get_next_filename(directory, base_filename)

    # Initialize the camera
    init_params = sl.InitParameters()
    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("Failed to open camera")
        return

    # Enable recording
    recording_params = sl.RecordingParameters(output_path, sl.SVO_COMPRESSION_MODE.H264)
    err = zed.enable_recording(recording_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Failed to start recording: {err}")
        zed.close()
        return

    print(f"Recording to {output_path}")

    # Capture frames and record them for 5 seconds
    start_time = time.time()
    while time.time() - start_time < 5:
        if zed.grab() != sl.ERROR_CODE.SUCCESS:
            print("Failed to grab frame")
            break

    zed.close()
    print(f"Recording finished. SVO file saved to {output_path}")
