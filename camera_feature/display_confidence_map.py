import sys
import numpy as np
import pyzed.sl as sl
import cv2
import os


def run():
    # Create a ZED camera object
    zed = sl.Camera()

    # Path to the folder containing the videos
    video_folder = os.path.join(os.path.dirname(__file__), '..', 'captured_videos')

    # List all SVO files in the directory
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.svo2')]

    if not video_files:
        print("No SVO files found in the directory.")
        exit(1)

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
        exit(1)

    input_file = os.path.join(video_folder, video_files[choice - 1])

    print(f"Playing confidence map video: {video_files[choice - 1]}")

    input_type = sl.InputType()
    input_type.set_from_svo_file(input_file)

    init = sl.InitParameters(input_t=input_type)
    init.camera_resolution = sl.RESOLUTION.HD1080
    init.depth_mode = sl.DEPTH_MODE.NEURAL
    init.coordinate_units = sl.UNIT.MILLIMETER

    err = zed.open(init)
    if err != sl.ERROR_CODE.SUCCESS:
        print(repr(err))
        zed.close()
        exit(1)

    runtime = sl.RuntimeParameters()
    image_size = zed.get_camera_information().camera_configuration.resolution

    confidence_map = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C1)

    key = ' '
    print('Press q to close the playback window')
    while key != 113:  # 'q' to quit
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_measure(confidence_map, sl.MEASURE.CONFIDENCE)
            confidence_np = confidence_map.get_data()
            normalized_confidence = cv2.normalize(confidence_np, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            colored_map = cv2.applyColorMap(normalized_confidence, cv2.COLORMAP_JET)

            cv2.imshow("Confidence Map", colored_map)

        elif err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
            print("End of file reached. Looping back.")
            zed.close()
            zed.open(init)

        key = cv2.waitKey(10)

    cv2.destroyAllWindows()
    zed.close()
    print("\nFINISH")


if __name__ == "__main__":
    run()
