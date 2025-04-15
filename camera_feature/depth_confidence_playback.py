import sys
import os
import numpy as np
import pyzed.sl as sl
import cv2

def run():
    zed = sl.Camera()

    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    video_folder = os.path.join(script_dir, '..', 'captured_videos')

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
        print("Invalid choice.")
        sys.exit(1)

    input_file = os.path.join(video_folder, video_files[choice - 1])
    print(f"Playing video: {video_files[choice - 1]}")

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

    runtime = sl.RuntimeParameters()
    camera_info = zed.get_camera_information().camera_configuration
    image_size = camera_info.resolution
    camera_fps = camera_info.fps
    frame_delay = int(1000 / camera_fps)

    image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    depth_image = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    confidence_map = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C1)

    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Depth", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Confidence Map", cv2.WINDOW_NORMAL)

    print("Press 'q' to quit.")
    key = ' '
    while key != 113:
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
            zed.retrieve_image(depth_image, sl.VIEW.DEPTH, sl.MEM.CPU, image_size)
            zed.retrieve_measure(confidence_map, sl.MEASURE.CONFIDENCE)

            image_ocv = image_zed.get_data()
            depth_ocv = depth_image.get_data()

            depth_ocv = cv2.normalize(depth_ocv, None, 0, 255, cv2.NORM_MINMAX)
            depth_ocv = cv2.convertScaleAbs(depth_ocv)

            confidence_np = confidence_map.get_data()
            normalized_confidence = cv2.normalize(confidence_np, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            colored_map = cv2.applyColorMap(normalized_confidence, cv2.COLORMAP_JET)

            cv2.imshow("Image", image_ocv)
            cv2.imshow("Depth", depth_ocv)
            cv2.imshow("Confidence Map", colored_map)

        elif err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
            print("End of file reached. Looping back.")
            zed.set_svo_position(0)

        key = cv2.waitKey(frame_delay)

    cv2.destroyAllWindows()
    zed.close()
    print("\nFINISH")

if __name__ == "__main__":
    run()
