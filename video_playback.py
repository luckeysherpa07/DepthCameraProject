import sys
import pyzed.sl as sl
import cv2
import os

def run():
    # Create a ZED camera object
    zed = sl.Camera()

    # Check if an SVO file path is provided
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    else:
        # If no argument, set default to "output.svo2"
        input_file = "output.svo2"

    # Ensure the file exists in the same directory
    if not os.path.isfile(input_file):
        print(f"Error: {input_file} not found.")
        exit(1)

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

    # Declare the image matrix
    image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)

    key = ' '
    while key != 113:  # 'q' to quit
        err = zed.grab(runtime)
        if err == sl.ERROR_CODE.SUCCESS:
            # Retrieve the left image from the SVO file
            zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)

            # Convert to OpenCV format
            image_ocv = image_zed.get_data()

            # Display the image in OpenCV window
            cv2.imshow("Image", image_ocv)

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
