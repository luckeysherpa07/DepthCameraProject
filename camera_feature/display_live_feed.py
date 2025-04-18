import sys
import numpy as np
import pyzed.sl as sl
import cv2
import os
import time

def get_next_filename(directory, base_filename):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return os.path.join(directory, f"{base_filename}_{timestamp}.svo")

def run():
    zed = sl.Camera()

    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "captured_videos")
    os.makedirs(directory, exist_ok=True)

    output_path = get_next_filename(directory, "captured_video")

    # Always use VGA resolution
    resolution = sl.RESOLUTION.VGA

    # # === Previous resolution selection code ===
    # resolutions = {
    #     "1": sl.RESOLUTION.HD2K,
    #     "2": sl.RESOLUTION.HD1080,
    #     "3": sl.RESOLUTION.HD720,
    #     "4": sl.RESOLUTION.VGA
    # }
    # print("Select ZED camera resolution:")
    # print("1. HD2K (2208x1242)")
    # print("2. HD1080 (1920x1080)")
    # print("3. HD720 (1280x720)")
    # print("4. VGA (672x376)")
    # res_input = input("Enter option number (1-4): ")
    # resolution = resolutions.get(res_input, sl.RESOLUTION.HD720)
    # ==========================================

    init_params = sl.InitParameters()
    init_params.camera_resolution = resolution
    init_params.camera_fps = 30
    init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init_params.coordinate_units = sl.UNIT.MILLIMETER

    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("Failed to open camera")
        return

    positional_tracking_params = sl.PositionalTrackingParameters()
    zed.enable_positional_tracking(positional_tracking_params)

    body_tracking_params = sl.BodyTrackingParameters()
    body_tracking_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_ACCURATE
    body_tracking_params.enable_tracking = True
    body_tracking_params.enable_body_fitting = True
    body_tracking_params.body_format = sl.BODY_FORMAT.BODY_34

    if zed.enable_body_tracking(body_tracking_params) != sl.ERROR_CODE.SUCCESS:
        print("Failed to enable body tracking.")
        zed.close()
        return

    cv2.namedWindow("RGB View", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Depth Map", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Confidence Map", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Body Tracking", cv2.WINDOW_NORMAL)

    cv2.moveWindow("RGB View", 0, 0)
    cv2.moveWindow("Depth Map", 640, 0)
    cv2.moveWindow("Confidence Map", 0, 480)
    cv2.moveWindow("Body Tracking", 640, 480)

    recording = False
    runtime_params = sl.RuntimeParameters()
    body_runtime_params = sl.BodyTrackingRuntimeParameters()
    body_runtime_params.detection_confidence_threshold = 40

    image = sl.Mat()
    depth = sl.Mat()
    confidence = sl.Mat()
    bodies = sl.Bodies()

    key = ' '
    print("Press 'q' to quit.")
    while key != 113:  # ASCII for 'q'
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            zed.retrieve_image(depth, sl.VIEW.DEPTH)
            zed.retrieve_measure(confidence, sl.MEASURE.CONFIDENCE)
            zed.retrieve_bodies(bodies, body_runtime_params)

            img_np = image.get_data()

            depth_map = cv2.normalize(depth.get_data(), None, 0, 255, cv2.NORM_MINMAX)
            depth_map = cv2.convertScaleAbs(depth_map)

            conf_map = cv2.normalize(confidence.get_data(), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            conf_map = cv2.applyColorMap(conf_map, cv2.COLORMAP_JET)

            cv2.imshow("RGB View", img_np)
            cv2.imshow("Depth Map", depth_map)
            cv2.imshow("Confidence Map", conf_map)

            for body in bodies.body_list:
                if body.tracking_state == sl.OBJECT_TRACKING_STATE.OK:
                    for kp in body.keypoint_2d:
                        if not np.isnan(kp[0]) and not np.isnan(kp[1]):
                            cv2.circle(img_np, (int(kp[0]), int(kp[1])), 3, (0, 255, 0), -1)

            if recording:
                cv2.putText(img_np, "REC", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Body Tracking", img_np)

            if key == 32:  # SPACE
                if not recording:
                    recording = True
                    recording_params = sl.RecordingParameters(output_path, sl.SVO_COMPRESSION_MODE.H264)
                    err = zed.enable_recording(recording_params)
                    if err != sl.ERROR_CODE.SUCCESS:
                        print(f"Failed to start recording: {err}")
                        zed.close()
                        return
                    print("Recording started...")
                else:
                    zed.disable_recording()
                    recording = False
                    print("Recording stopped.")

        key = cv2.waitKey(10)

    zed.close()
    cv2.destroyAllWindows()
    print(f"SVO file saved to {output_path}")
    print("\nFINISH")

if __name__ == "__main__":
    run()
