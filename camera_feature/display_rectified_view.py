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

    # Enable tracking and body tracking
    zed.enable_positional_tracking(sl.PositionalTrackingParameters())
    body_tracking_params = sl.BodyTrackingParameters()
    body_tracking_params.detection_model = sl.BODY_TRACKING_MODEL.HUMAN_BODY_ACCURATE
    body_tracking_params.enable_tracking = True
    body_tracking_params.enable_body_fitting = True
    body_tracking_params.body_format = sl.BODY_FORMAT.BODY_34
    if zed.enable_body_tracking(body_tracking_params) != sl.ERROR_CODE.SUCCESS:
        print("Failed to enable body tracking.")
        zed.close()
        return

    # Load stereo calibration
    calib = np.load("stereo_calibration.npz")
    K1 = calib['cameraMatrix1']
    D1 = calib['distCoeffs1']
    K2 = calib['cameraMatrix2']
    D2 = calib['distCoeffs2']
    R = calib['R']
    T = calib['T']
    img_size = tuple(calib['imageSize'])

    # Compute rectification maps for ZED image (assuming ZED = camera 2)
    R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(K1, D1, K2, D2, img_size, R, T, flags=cv2.CALIB_ZERO_DISPARITY)
    map1, map2 = cv2.initUndistortRectifyMap(K2, D2, R2, P1, img_size, cv2.CV_16SC2)

    cv2.namedWindow("Aligned ZED to DAVIS View", cv2.WINDOW_NORMAL)
    cv2.moveWindow("Aligned ZED to DAVIS View", 100, 100)

    recording = False
    runtime_params = sl.RuntimeParameters()
    body_runtime_params = sl.BodyTrackingRuntimeParameters()
    body_runtime_params.detection_confidence_threshold = 40

    image = sl.Mat()
    bodies = sl.Bodies()
    key = ' '

    print("Press 'q' to quit.")
    while key != 113:  # ASCII for 'q'
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image, sl.VIEW.LEFT)
            zed.retrieve_bodies(bodies, body_runtime_params)
            img_np = image.get_data()

            # Resize to match calibration image size
            img_np = cv2.resize(img_np, img_size)

            # Rectify the ZED image to align with DAVIS view
            aligned_zed = cv2.remap(img_np, map1, map2, cv2.INTER_LINEAR)

            # Draw body keypoints
            for body in bodies.body_list:
                if body.tracking_state == sl.OBJECT_TRACKING_STATE.OK:
                    for kp in body.keypoint_2d:
                        if not np.isnan(kp[0]) and not np.isnan(kp[1]):
                            x, y = int(kp[0]), int(kp[1])
                            if 0 <= x < img_size[0] and 0 <= y < img_size[1]:
                                cv2.circle(aligned_zed, (x, y), 3, (0, 255, 0), -1)

            if recording:
                cv2.putText(aligned_zed, "REC", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Aligned ZED to DAVIS View", aligned_zed)

            # Start/stop recording
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
