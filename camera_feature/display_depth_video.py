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

    print(f"Playing video: {video_files[choice - 1]}")

    input_type = sl.InputType()
    input_type.set_from_svo_file(input_file)

    init = sl.InitParameters(input_t=input_type)
    init.camera_resolution = sl.RESOLUTION.HD1080  # Set your preferred resolution
    init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init.coordinate_units = sl.UNIT.MILLIMETER

    # Open the ZED camera or load the SVO file
    err = zed.open(init)
    if err != sl.ERROR_CODE.SUCCESS:
        print(repr(err))
        zed.close()
        exit(1)

    # Prepare runtime parameters
    runtime = sl.RuntimeParameters()

    # Get the resolution of the SVO file
    image_size = zed.get_camera_information().camera_configuration.resolution

    # Declare the image matrix for depth data
    depth_image = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)

    key = ' '
    while key != 113:  # 'q' to quit
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            # Retrieve the depth image from the SVO file
            zed.retrieve_image(depth_image, sl.VIEW.DEPTH, sl.MEM.CPU, image_size)

            # Convert depth data to OpenCV format
            depth_ocv = depth_image.get_data()

            # Normalize depth image for better visualization (optional)
            depth_ocv = cv2.normalize(depth_ocv, None, 0, 255, cv2.NORM_MINMAX)
            depth_ocv = cv2.convertScaleAbs(depth_ocv)

            # Display the depth image in OpenCV window
            cv2.imshow("Depth Image", depth_ocv)

        # Check if the end of the SVO file is reached and reset
        elif err == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
            print("End of file reached. Looping back.")

            # Close and reopen the SVO file to reset playback
            zed.close()
            zed.open(init)  # Reopen the file from the beginning

        # Wait for a key press to continue
        key = cv2.waitKey(10)

    cv2.destroyAllWindows()
    zed.close()
    print("\nFINISH")

if __name__ == "__main__":
    run()
