import numpy as np
import cv2
import pyzed.sl as sl  # Correct import

# Initialize ZED camera
zed = sl.Camera()

# Set configuration parameters
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD1080  # Adjust resolution
init_params.camera_fps = 30  # Frame rate

# Open the camera
if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
    print("Unable to open ZED camera")
    exit()

# Create objects to hold images
image_rgb = sl.Mat()
image_depth = sl.Mat()

# Grab a frame from the camera
runtime_parameters = sl.RuntimeParameters()
while True:
    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image_rgb, sl.VIEW.LEFT)  # Get RGB frame
        zed.retrieve_measure(image_depth, sl.MEASURE.DEPTH)  # Get depth data

        # Convert to numpy arrays
        rgb = np.asarray(image_rgb.get_data())
        depth = image_depth.get_data()

        # Handle invalid depth values
        depth[depth <= 0] = np.nan  # Set invalid depths to NaN

        # Replace NaN with 0 and ensure it's a NumPy array
        depth_colored = np.nan_to_num(depth, nan=0)  

        # Check if depth_colored is a 2D array
        if len(depth_colored.shape) != 2:
            print("Depth data is not 2D, reshaping...")
            depth_colored = depth_colored[:, :, 0]  # Get just one channel if it's 3D

        # Ensure depth_colored is a valid numpy array
        if not isinstance(depth_colored, np.ndarray):
            print("depth_colored is not a NumPy array")
            continue

        print("Depth Collected Type:", type(depth_colored))
        print("Depth Collected Shape:", depth_colored.shape)

        # Check if depth_colored has valid data
        if np.any(np.isnan(depth_colored)):
            print("depth_colored contains NaN values")

        # Normalize and colorize depth image
        depth_colored = np.clip(depth_colored, 0, 10)  # Clip depth range to 0-10 meters

        # Check if depth_colored is now a valid NumPy array
        # if isinstance(depth_colored, np.ndarray):
        #     depth_colored = cv2.normalize(depth_colored, None, 0, 255, cv2.NORM_MINMAX)  # Normalize depth
        #     depth_colored = np.uint8(depth_colored)  # Convert to uint8 for colormap
        #     depth_colored = cv2.applyColorMap(depth_colored, cv2.COLORMAP_JET)  # Apply color map
        # else:
        #     print("Error: depth_colored is not a valid NumPy array")
        #     continue

        # Check if rgb is a valid NumPy array
        if rgb is None or not isinstance(rgb, np.ndarray):
            print("Error: RGB image is not a valid NumPy array")
            continue

        # Check the shape and type
        print("RGB Image Type:", type(rgb))
        print("RGB Image Shape:", rgb.shape)

        # Ensure it's a uint8 type
        if rgb.dtype != np.uint8:
            rgb = rgb.astype(np.uint8)

        # Remove alpha channel if it exists (RGBA -> RGB)
        if rgb.shape[-1] == 4:
            rgb = rgb[..., :3]

        # Convert color format if needed (BGRA to BGR)
        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGRA2BGR)

        # Display images
        cv2.imshow("RGB Image", rgb)
        # cv2.imshow("Depth Image", depth_colored)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
zed.close()
cv2.destroyAllWindows()
