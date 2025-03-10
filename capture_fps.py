import sys
import pyzed.sl as sl

def run():
    # Create a ZED camera object
    zed = sl.Camera()

    # Set SVO file path
    input_path = "output.svo2"  # The path to the SVO file

    # Set up initialization parameters for playback
    init_parameters = sl.InitParameters()
    init_parameters.set_from_svo_file(input_path)

    # Open the ZED camera
    err = zed.open(init_parameters)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Failed to open the SVO file")
        exit(1)

    # Get the FPS of the SVO file
    fps = zed.get_camera_information().camera_configuration.fps
    print(f"FPS of the SVO file: {fps}")

    # Close the camera after use
    zed.close()
