import sys
import numpy as np
import pyzed.sl as sl
import cv2
import os
import time
import multiprocessing

def get_next_filename(directory, base_filename):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return os.path.join(directory, f"{base_filename}_{timestamp}.svo")

def run(recording_flag):
    zed = sl.Camera()

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captured_videos")
    os.makedirs(directory, exist_ok=True)

    output_path = get_next_filename(directory, "captured_video")

    resolution = sl.RESOLUTION.VGA

    init_params = sl.InitParameters()
    init_params.camera_resolution = resolution
    init_params.camera_fps = 30
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL
    init_params.coordinate_units = sl.UNIT.MILLIMETER

    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("Failed to open camera")
        return

    cv2.namedWindow("RGB View", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Depth Map", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Confidence Map", cv2.WINDOW_NORMAL)

    # Set window positions
    cv2.moveWindow("RGB View", 0, 0)
    cv2.moveWindow("Depth Map", 640, 0)
    cv2.moveWindow("Confidence Map", 0, 480)

    recording = False
    runtime_params = sl.RuntimeParameters()

    image = sl.Mat()
    depth = sl.Mat()
    confidence = sl.Mat()

    key = ' '
    print("Press 'q' to quit.")
    while key != 113:  # ASCII for 'q'
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            zed.retrieve_image(depth, sl.VIEW.DEPTH)
            zed.retrieve_measure(confidence, sl.MEASURE.CONFIDENCE)

            img_np = image.get_data()

            # FoV adjustment (ZED -> DAVIS)
            zoom_factor = 3.0

            h, w, _ = img_np.shape
            zoom_w = int(w / zoom_factor)
            zoom_h = int(h / zoom_factor)

            start_x = (w - zoom_w) // 2
            start_y = (h - zoom_h) // 2
            img_np = img_np[start_y:start_y + zoom_h, start_x:start_x + zoom_w]

            # Resize while preserving aspect ratio
            target_aspect_ratio = 1.33
            window_width = 1280
            window_height = 720

            new_height = int(window_width / target_aspect_ratio)
            if new_height > window_height:
                new_height = window_height
                new_width = int(new_height * target_aspect_ratio)
            else:
                new_width = window_width

            img_resized = cv2.resize(img_np, (new_width, new_height))

            # Depth map
            depth_data = depth.get_data()
            if depth_data is None:
                continue
            depth_map = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX)
            depth_map = cv2.convertScaleAbs(depth_map)
            depth_map = depth_map[start_y:start_y + zoom_h, start_x:start_x + zoom_w]
            depth_map = cv2.resize(depth_map, (new_width, new_height))

            # Confidence map
            conf_data = confidence.get_data()
            if conf_data is None:
                continue
            conf_map = cv2.normalize(conf_data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            conf_map = cv2.applyColorMap(conf_map, cv2.COLORMAP_JET)
            conf_map = conf_map[start_y:start_y + zoom_h, start_x:start_x + zoom_w]
            conf_map = cv2.resize(conf_map, (new_width, new_height))

            if recording:
                cv2.putText(img_resized, "REC", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("RGB View", img_resized)
            cv2.imshow("Depth Map", depth_map)
            cv2.imshow("Confidence Map", conf_map)

            if recording_flag.value and not recording:
                recording = True
                recording_params = sl.RecordingParameters(output_path, sl.SVO_COMPRESSION_MODE.H264)
                err = zed.enable_recording(recording_params)
                if err != sl.ERROR_CODE.SUCCESS:
                    print(f"Failed to start recording: {err}")
                    zed.close()
                    return
                print("Recording started...")

            if not recording_flag.value and recording:
                zed.disable_recording()
                recording = False
                print("Recording stopped.")

        key = cv2.waitKey(10)

    zed.close()
    cv2.destroyAllWindows()
    print(f"SVO file saved to {output_path}")
    print("\nFINISH")

if __name__ == "__main__":
    recording_flag = multiprocessing.Value('b', False)
    process2 = multiprocessing.Process(target=run, args=(recording_flag,))
    process2.start()

    while True:
        time.sleep(5)
        recording_flag.value = not recording_flag.value
        print(f"Recording Flag: {recording_flag.value}")
        if not process2.is_alive():
            break
