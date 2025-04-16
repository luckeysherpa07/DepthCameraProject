import sys
import os
import numpy as np
import pyzed.sl as sl
import cv2

def run():
    zed = sl.Camera()

    # Folder setup and video file selection
    video_folder = os.path.join(os.path.dirname(__file__), '..', 'captured_videos')
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.svo2')]

    if not video_files:
        print("No SVO files found in the directory.")
        sys.exit(1)

    print("Available video files:")
    for idx, video in enumerate(video_files, 1):
        print(f"{idx}. {video}")

    choice = input(f"Select a video (1-{len(video_files)}): ")
    try:
        choice = int(choice)
        if not (1 <= choice <= len(video_files)):
            raise ValueError
    except ValueError:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    input_file = os.path.join(video_folder, video_files[choice - 1])
    print(f"Playing video: {video_files[choice - 1]}")

    # Input and initialization parameters
    input_type = sl.InputType()
    input_type.set_from_svo_file(input_file)

    init = sl.InitParameters(input_t=input_type)
    init.camera_resolution = sl.RESOLUTION.HD1080
    init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init.coordinate_units = sl.UNIT.MILLIMETER

    if zed.open(init) != sl.ERROR_CODE.SUCCESS:
        print("ZED initialization failed.")
        zed.close()
        sys.exit(1)

    # Enable positional and body tracking
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
        sys.exit(1)

    runtime_params = sl.RuntimeParameters()
    body_runtime_params = sl.BodyTrackingRuntimeParameters()
    body_runtime_params.detection_confidence_threshold = 40

    # Image and data setup
    image_zed = sl.Mat()
    depth_image = sl.Mat()
    confidence_map = sl.Mat()
    bodies = sl.Bodies()

    # OpenCV window setup
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Depth", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Confidence Map", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Body Tracking", cv2.WINDOW_NORMAL)

    print("Press 'q' to quit.")
    key = ' '
    while key != 113:  # ASCII for 'q'
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # Retrieve images and depth data
            zed.retrieve_image(image_zed, sl.VIEW.LEFT)
            zed.retrieve_image(depth_image, sl.VIEW.DEPTH)
            zed.retrieve_measure(confidence_map, sl.MEASURE.CONFIDENCE)
            zed.retrieve_bodies(bodies, body_runtime_params)

            image_ocv = image_zed.get_data()
            depth_ocv = depth_image.get_data()

            # Normalize and convert depth image
            depth_ocv = cv2.normalize(depth_ocv, None, 0, 255, cv2.NORM_MINMAX)
            depth_ocv = cv2.convertScaleAbs(depth_ocv)

            # Process confidence map
            confidence_np = confidence_map.get_data()
            normalized_confidence = cv2.normalize(confidence_np, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            colored_map = cv2.applyColorMap(normalized_confidence, cv2.COLORMAP_JET)

            # Copy for keypoint drawing
            image_with_keypoints = image_ocv.copy()

            # Draw body keypoints only on the copy
            for body in bodies.body_list:
                if body.tracking_state == sl.OBJECT_TRACKING_STATE.OK:
                    for kp in body.keypoint_2d:
                        if not np.isnan(kp[0]) and not np.isnan(kp[1]):
                            cv2.circle(image_with_keypoints, (int(kp[0]), int(kp[1])), 3, (0, 255, 0), -1)

            # Show the images
            cv2.imshow("Image", image_ocv)  # clean RGB image
            cv2.imshow("Depth", depth_ocv)
            cv2.imshow("Confidence Map", colored_map)
            cv2.imshow("Body Tracking", image_with_keypoints)  # with keypoints

        elif zed.get_svo_position() == zed.get_svo_end_position():
            print("End of file reached. Looping back.")
            zed.set_svo_position(0)

        key = cv2.waitKey(10)

    # Cleanup
    cv2.destroyAllWindows()
    zed.close()
    print("\nFINISH")

if __name__ == "__main__":
    run()
