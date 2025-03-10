import sys
import pyzed.sl as sl

def run():
    # Create a ZED camera object
    zed = sl.Camera()

    # Set SVO path for playback from command line argument
    input_path = "output.svo2"
    
    # Initialize parameters for SVO playback
    init_parameters = sl.InitParameters()
    init_parameters.set_from_svo_file(input_path)

    # Open the ZED camera
    err = zed.open(init_parameters)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Failed to open camera")
        return

    print(f"Playing back SVO file: {input_path}")
    
    # Initialize image to store frames
    svo_image = sl.Mat()

    # Exit condition flag
    exit_app = False

    # Loop to grab and process frames
    while not exit_app:
        # Grab the next frame
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            # Retrieve the side-by-side image from the SVO file
            zed.retrieve_image(svo_image, sl.VIEW.SIDE_BY_SIDE)
            # Get the current position in the SVO
            svo_position = zed.get_svo_position()
            print(f"Current SVO position: {svo_position}")
            
            # You can add additional processing here if needed

        elif zed.grab() == sl.ERROR_CODE.END_OF_SVOFILE_REACHED:
            print("SVO end has been reached. Looping back to first frame.")
            zed.set_svo_position(0)  # Loop back to the first frame

        # Add exit condition based on your needs, for example, a specific time or key press
        # Here, you can set exit_app = True based on a condition or time
