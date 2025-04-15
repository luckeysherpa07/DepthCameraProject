import pyzed.sl as sl
import time
import os
import cv2

def get_next_filename(directory, base_filename):
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

def run():
    zed = sl.Camera()

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captured_videos")
    if not os.path.exists(directory):
        os.makedirs(directory)

    base_filename = "captured_video"
    output_path = get_next_filename(directory, base_filename)

    resolution = select_resolution()

    init_params = sl.InitParameters()
    init_params.camera_resolution = resolution
    init_params.camera_fps = 30

    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("Failed to open camera")
        return

    cv2.namedWindow("ZED Live View", cv2.WINDOW_NORMAL)

    recording_params = sl.RecordingParameters(output_path, sl.SVO_COMPRESSION_MODE.H264)
    err = zed.enable_recording(recording_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Failed to start recording: {err}")
        zed.close()
        return

    print(f"Recording is ready. Press SPACE to start/stop. Press ESC to exit.")

    recording = False

    while True:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            image = sl.Mat()
            zed.retrieve_image(image, sl.VIEW.LEFT)
            image_data = image.get_data()

            if recording:
                cv2.putText(image_data, "REC", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("ZED Live View", image_data)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == 32:  # SPACE
                recording = not recording
                print("Recording started..." if recording else "Recording stopped.")

    zed.disable_recording()
    zed.close()
    cv2.destroyAllWindows()
    print(f"SVO file saved to {output_path}")

if __name__ == "__main__":
    run()
