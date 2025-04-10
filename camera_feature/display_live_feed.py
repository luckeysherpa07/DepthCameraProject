import pyzed.sl as sl
import cv2

def run():
    # Set up the ZED camera
    zed = sl.Camera()

    # Initialize ZED camera parameters
    init = sl.InitParameters()
    init.camera_resolution = sl.RESOLUTION.HD720  # Choose your resolution (e.g., HD720)
    init.depth_mode = sl.DEPTH_MODE.NONE  # No depth information needed for live view

    # Open the camera
    if zed.open(init) != sl.ERROR_CODE.SUCCESS:
        print("Failed to open camera")
        exit(1)

    # Create a Mat object to store images
    image = sl.Mat()

    # Create a resizable OpenCV window
    cv2.namedWindow("ZED Live View", cv2.WINDOW_NORMAL)
    
    print("Press ESC to exit.")
    while True:
        # Grab the latest frame
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            # Retrieve the left image from the camera
            zed.retrieve_image(image, sl.VIEW.LEFT)

            # Convert image to OpenCV format and show it
            image_data = image.get_data()
            cv2.imshow("ZED Live View", image_data)

            # Wait for the ESC key to exit
            if cv2.waitKey(1) == 27:  # ESC key
                break

    # Close the camera and OpenCV windows
    zed.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run()
