import pyzed.sl as sl
import time
import os

def get_next_filename(directory, base_filename):
    # Generate a unique filename using the current timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return os.path.join(directory, f"{base_filename}_{timestamp}.svo")

def run():
    # Create a ZED camera object
    zed = sl.Camera()

    # Define the base path and filename
    directory = os.path.dirname(os.path.abspath(__file__))
    base_filename = "captured_video"

    # Get the next available filename with a unique timestamp
    output_path = get_next_filename(directory, base_filename)

    # Initialize the camera
    init_params = sl.InitParameters()

    # Specify the resolution (e.g., HD 720p)
    init_params.camera_resolution = sl.RESOLUTION.HD720  # Options: HD2K, HD1080, HD720, VGA
    init_params.camera_fps = 30  # Set frames per second (adjust as needed)

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

    # Disable recording and close the camera
    zed.disable_recording()
    zed.close()
    print(f"Recording finished. SVO file saved to {output_path}")

if __name__ == "__main__":
    run()
