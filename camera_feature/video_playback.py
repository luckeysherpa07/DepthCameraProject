import sys
import pyzed.sl as sl
import cv2
import os

def run():
    # Create a ZED camera object
    zed = sl.Camera()

    # Path to the folder containing the videos, go one level up from the current directory
    video_folder = os.path.join(os.path.dirname(__file__), '..', 'captured_videos')

    # List all SVO files in the directory
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.svo2')]

    if not video_files:
        print("No SVO files found in the directory.")
        sys.exit(1)

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
        sys.exit(1)

    input_file = os.path.join(video_folder, video_files[choice - 1])

    print(f"Playing video: {video_files[choice - 1]}")

    input_type = sl.InputType()
    input_type.set_from_svo_file(input_file)

    init = sl.InitParameters(input_t=input_type)
    init.camera_resolution = sl.RESOLUTION.HD1080
    init.depth_mode = sl.DEPTH_MODE.NEURAL
    init.coordinate_units = sl.UNIT.MILLIMETER

    # Open the ZED camera or load the SVO file
    err = zed.open(init)
    if err != sl.ERROR_CODE.SUCCESS:
        print(repr(err))
        zed.close()
        sys.exit(1)

    # Get original recording FPS and compute delay for real-time playback
    camera_fps = zed.get_camera_information().camera_configuration.fps
    frame_delay = int(1000 / camera_fps)  # in milliseconds

    # Prepare runtime parameters
    runtime = sl.RuntimeParameters()

    # Get the resolution of the SVO file
    image_size = zed.get_camera_information().camera_configuration.resolution

    # Declare the image matrix
    image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)

    cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)
    key = ' '
    print('Press q to close the playback window')

    while key != 113:  # 'q' to quit
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
            image_ocv = image_zed.get_data()
            cv2.imshow("Image", image_ocv)
        elif err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
            print("End of file reached. Looping back.")
            zed.set_svo_position(0)
            continue

        key = cv2.waitKey(frame_delay)

    cv2.destroyAllWindows()
    zed.close()
    print("\nFINISH")

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nPlayback interrupted by user.")
