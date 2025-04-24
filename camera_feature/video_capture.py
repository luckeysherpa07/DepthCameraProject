import pyzed.sl as sl
import time
import os

def get_next_filename(directory, base_filename):
    # Generate a unique filename using the current timestamp (avoid invalid characters like ":")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return os.path.join(directory, f"{base_filename}_{timestamp}.svo")

def select_resolution():
    print("Select a resolution:")
    print("1: HD2K (2208x1242)")
    print("2: HD1080 (1920x1080)")
    print("3: HD720 (1280x720)")
    print("4: VGA (640x480)")

    choice = input("Enter the number of your choice (1-4): ")

    resolutions = {
        "1": sl.RESOLUTION.HD2K,
        "2": sl.RESOLUTION.HD1080,
        "3": sl.RESOLUTION.HD720,
        "4": sl.RESOLUTION.VGA,
    }

    return resolutions.get(choice, sl.RESOLUTION.HD720)

def run(duration=5):
    # Create a ZED camera object
    zed = sl.Camera()

    # Define the base path and filename (one directory above the script)
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captured_videos")
    if not os.path.exists(directory):
        os.makedirs(directory)  # Create directory if it doesn't exist
    base_filename = "captured_video"

    # Get the next available filename with a unique timestamp
    output_path = get_next_filename(directory, base_filename)

    # Select resolution from user input
    resolution = select_resolution()

    # Initialize the camera
    init_params = sl.InitParameters()
    init_params.camera_resolution = resolution
    init_params.camera_fps = 30

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

    # Capture frames and record for the given duration
    start_time = time.time()
    while time.time() - start_time < duration:
        if zed.grab() != sl.ERROR_CODE.SUCCESS:
            print("Failed to grab frame")
            break

    # Disable recording and close the camera
    zed.disable_recording()
    zed.close()
    print(f"Recording finished. SVO file saved to {output_path}")

if __name__ == "__main__":
    run()
