import pyzed.sl as sl
import numpy as np
import cv2
import os
import time
# You will need dv_processing installed and accessible in this single process
import dv_processing as dv # Assuming dv_processing is used for DAVIS

def run():
    # --- Configuration ---
    # Define pattern dimensions and spacing
    NUM_ROWS = 4
    NUM_COLS = 5
    SPACING_MM = 50.0 # Spacing between circle centers in millimeters
    NUM_POINTS = NUM_ROWS * NUM_COLS

    # Target number of successful views for calibration
    TARGET_CALIBRATION_VIEWS = 20

    # --- 1. Define the physical pattern 3D points (objp) ---
    # This is based on your 4x5 circle grid with 50mm spacing.
    # This array represents the 3D coordinates of the pattern points
    # in the pattern's own coordinate system (assuming Z=0).
    objp = np.zeros((NUM_POINTS, 3), np.float32)
    objp[:, :2] = np.mgrid[0:NUM_COLS, 0:NUM_ROWS].T.reshape(-1, 2) * SPACING_MM

    print("Calculated the 3D template for one view (objp).")


    # --- 2. Load Intrinsic Parameters for ZED (Left) and DAVIS ---

    # --- ZED Camera Setup and Intrinsics ---
    print("Initializing ZED Camera and getting intrinsics...")
    zed_camera_matrix = None
    zed_dist_coeffs = None
    zed_image_size = None

    zed = sl.Camera()
    init_params_zed = sl.InitParameters()
    # Set the resolution you will use for STEREO calibration capture.
    # This MUST match the resolution used for ZED intrinsic calibration
    # AND the resolution you can capture from the DAVIS camera.
    # Using VGA (672x376) as an example, based on your previous code.
    init_params_zed.camera_resolution = sl.RESOLUTION.VGA # Set ZED to VGA (672x376)
    init_params_zed.sdk_verbose = 0
    init_params_zed.depth_mode = sl.DEPTH_MODE.NONE # Depth not needed for calibration

    # Open the camera
    err_zed = zed.open(init_params_zed)
    if err_zed != sl.ERROR_CODE.SUCCESS:
        print(f"Error {err_zed}: Failed to open ZED camera.")
        return # Use return instead of exit() inside a function

    # Get intrinsic parameters for the opened resolution
    cam_info = zed.get_camera_information()
    calib = cam_info.camera_configuration.calibration_parameters
    left_cam = calib.left_cam

    zed_camera_matrix = np.array([
        [left_cam.fx, 0, left_cam.cx],
        [0, left_cam.fy, left_cam.cy],
        [0, 0, 1]
    ])

    # Ensure disto has at least 5 elements for cv2 functions
    disto = left_cam.disto
    if len(disto) < 5:
        disto = disto + [0.0] * (5 - len(disto)) # Pad with zeros if less than 5
    zed_dist_coeffs = np.array(disto, dtype=np.float64)

    # Get the actual image size corresponding to the resolution used
    camera_resolution = cam_info.camera_configuration.resolution
    zed_image_size = (int(camera_resolution.width), int(camera_resolution.height))

    print("ZED Camera Matrix (Left):\n", zed_camera_matrix)
    print("\nZED Distortion Coefficients (Left):\n", zed_dist_coeffs)
    print(f"\nZED Image Size used for these intrinsics: {zed_image_size}")

    # Keep ZED open for capturing frames later


    print("-" * 40)

    # --- DAVIS Camera Setup and Intrinsics ---
    print("Initializing DAVIS Camera and loading intrinsics from XML...")
    davis_camera_matrix = None
    davis_dist_coeffs = None
    # Image size used for DAVIS intrinsic calibration AND stereo calibration capture.
    # This MUST match the ZED resolution set above.
    # Setting to match ZED VGA (672x376)
    davis_image_size = (672, 376) # <-- Set DAVIS assumed resolution to match ZED VGA

    # --- Initialize DAVIS Camera using dv_processing ---
    davis_camera_initialized = False
    davis_camera = None # Initialize davis_camera to None
    try:
        # Open the camera, just use first detected DAVIS camera
        davis_camera = dv.io.CameraCapture("", dv.io.CameraCapture.CameraType.DAVIS)
        davis_camera_initialized = True
        # IMPORTANT: You MUST ensure your physical DAVIS camera is configured
        # to output frames at the resolution specified in davis_image_size (672x376)
        # using your dv_processing setup outside of this script's initialization.
        print(f"DAVIS camera initialized using dv_processing. Assuming resolution {davis_image_size[0]}x{davis_image_size[1]}.")

    except Exception as e:
        print(f"Error initializing DAVIS camera using dv_processing: {e}")
        # Cleanup ZED if DAVIS fails
        zed.close()
        return # Use return instead of exit()

    if not davis_camera_initialized:
         print("Failed to initialize DAVIS camera. Exiting.")
         zed.close()
         return # Use return instead of exit()


    # --- Load DAVIS Intrinsics from XML ---
    # Construct path by getting the absolute path of the script's directory,
    # then its parent directory, and then joining the calibration file path.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir) # Go up one directory from the script's directory
    # Corrected filename: davis_intrinsics.xml (added 's')
    file_path = os.path.abspath(os.path.join(parent_dir, "DAVIS_calibration_file", "davis_intrinsics.xml"))

    print(f"Attempting to load DAVIS intrinsics from: {file_path}") # Print the constructed path


    if not os.path.isfile(file_path):
        print(f"\nDAVIS intrinsics file not found at: {file_path}")
        # Cleanup and exit if intrinsics file is missing
        zed.close()
        if davis_camera: davis_camera = None # Cleanup DAVIS if initialized
        return # Use return instead of exit()
    else:
        fs = cv2.FileStorage(file_path, cv2.FILE_STORAGE_READ)
        if not fs.isOpened():
            print(f"\nFailed to open DAVIS intrinsics file: {file_path}")
            # Cleanup and exit
            fs.release()
            zed.close()
            if davis_camera: davis_camera = None
            return # Use return instead of exit()
        else:
            # Assuming the node name is constant as in your example
            camera_node = fs.getNode("DAVIS346_00000001")
            if not camera_node:
                 print(f"\nError: Camera node 'DAVIS346_00000001' not found in {file_path}")
                 # Cleanup and exit
                 fs.release()
                 zed.close()
                 if davis_camera: davis_camera = None
                 return # Use return instead of exit()
            else:
                cm_node = camera_node.getNode("camera_matrix")
                dc_node = camera_node.getNode("distortion_coefficients")
                size_node = camera_node.getNode("image_size") # Assuming image_size is also stored

                if not cm_node or not dc_node:
                     print(f"\nError: Camera matrix or distortion coefficients not found under the camera node in {file_path}")
                     # Cleanup and exit
                     fs.release()
                     zed.close()
                     if davis_camera: davis_camera = None
                     return # Use return instead of exit()
                else:
                    davis_camera_matrix = cm_node.mat()
                    davis_dist_coeffs = dc_node.mat() # Ensure dtype is float64 if needed by cv2 functions later

                    # Try to get image size from the file if available
                    davis_image_size_from_file = None
                    if size_node and size_node.isSeq():
                        size_seq = size_node.mat() # Reads as a 1x2 or 2x1 matrix usually
                        if size_seq.shape == (1, 2):
                             davis_image_size_from_file = (int(size_seq[0,0]), int(size_seq[0,1]))
                        elif size_seq.shape == (2, 1):
                             davis_image_size_from_file = (int(size_seq[0,0]), int(size_seq[1,0]))
                        else:
                             print("Warning: Could not interpret image_size format in XML.")

                    else:
                        print("Warning: image_size node not found or not a sequence/matrix in XML.")


                    print("\nDAVIS Camera Matrix:\n", davis_camera_matrix)
                    print("\nDAVIS Distortion Coefficients:\n", davis_dist_coeffs)
                    if davis_image_size_from_file:
                        print(f"\nDAVIS Image Size from XML intrinsics: {davis_image_size_from_file}")
                        # Verify this matches the size you are capturing at!
                        if davis_image_size_from_file != davis_image_size:
                             print(f"ERROR: DAVIS capture resolution ({davis_image_size}) does not match resolution from intrinsics file ({davis_image_size_from_file}).")
                             print("You must use the same resolution for intrinsic calibration and stereo calibration capture.")
                             # Cleanup and exit
                             fs.release()
                             zed.close()
                             if davis_camera: davis_camera = None
                             return # Use return instead of exit()
                    else:
                        print("\nWarning: Could not determine DAVIS image size from XML. Assuming your capture resolution matches the one used for intrinsic calibration.")
                        # You MUST be sure that the 'davis_image_size' variable above
                        # matches the resolution used for the intrinsics in the XML file.


            fs.release()


    # --- Ensure capture resolutions match for stereo calibration function input ---
    # cv2.stereoCalibrate expects a single imageSize parameter.
    # This implies the calibration images you collected must be the same size.
    if zed_image_size != davis_image_size:
        print("\nERROR: ZED and DAVIS capture resolutions are not set to be the same!")
        print(f" ZED resolution: {zed_image_size}")
        print(f" DAVIS resolution: {davis_image_size}")
        print("Stereo calibration requires images of the same size.")
        print("Please adjust camera settings or code to ensure consistent resolution.")
        # Cleanup and exit
        zed.close()
        if davis_camera: davis_camera = None
        return # Use return instead of exit()

    # Image size to use for cv2.stereoCalibrate
    imageSize_for_stereo = zed_image_size # Since they must be the same


    print("-" * 40)

    # --- Prepare the lists for calibration input ---
    # These lists will be populated during the capture loop.
    objectPoints_list = [] # List of objp arrays (one for each successful view)
    imagePoints1_list = [] # List of 2D points from Camera 1 (DAVIS)
    imagePoints2_list = [] # List of 2D points from Camera 2 (ZED Left)


    # --- Main Synchronized Capture Loop ---
    print("\nStarting synchronized capture loop for stereo calibration data...")
    print(f"Target number of successful views: {TARGET_CALIBRATION_VIEWS}")
    print("Move the pattern to different positions and orientations.")
    print("Press 'c' to CAPTURE a frame pair and attempt pattern detection.")
    print("Press 'q' to QUIT.")


    # Create OpenCV windows for preview
    cv2.namedWindow("DAVIS View", cv2.WINDOW_NORMAL)
    cv2.namedWindow("ZED Left View", cv2.WINDOW_NORMAL)

    # ZED image object for grabbing
    image_zed = sl.Mat()
    runtime_params_zed = sl.RuntimeParameters()


    while len(objectPoints_list) < TARGET_CALIBRATION_VIEWS:
        # --- Synchronized Capture Attempt ---
        # The goal is to get frames from BOTH cameras as close in time as possible.
        # The exact method depends on your hardware and SDKs.
        # A simple approach is to try grabbing from both in quick succession.
        # A better approach involves hardware triggers if available.

        # Grab from ZED
        err_zed_grab = zed.grab(runtime_params_zed)

        # Grab from DAVIS using dv_processing
        # --- REPLACE THIS WITH YOUR ACTUAL DAVIS FRAME CAPTURE CODE ---
        # You need to get a single frame from the DAVIS camera here.
        # Example using getNextFrame() which might block or return None
        davis_frame = davis_camera.getNextFrame() # This gets the latest frame available

        # Check if both grabs were successful
        if err_zed_grab == sl.ERROR_CODE.SUCCESS and davis_frame is not None:
            # Both frames are (assumed) captured. Now process them.

            # Retrieve ZED left image
            zed.retrieve_image(image_zed, sl.VIEW.LEFT)
            zed_cv_image = image_zed.get_data() # Get numpy array (BGRA)
            zed_cv_image = cv2.cvtColor(zed_cv_image, cv2.COLOR_BGRA2BGR) # Convert to BGR for OpenCV

            # Convert DAVIS frame to OpenCV image (NumPy array)
            # dv_processing frames have an 'image' attribute
            davis_cv_image = davis_frame.image
            # Ensure it's BGR (convert if grayscale)
            if len(davis_cv_image.shape) == 2:
                davis_cv_image = cv2.cvtColor(davis_cv_image, cv2.COLOR_GRAY2BGR)


            # --- Pattern Detection ---
            # Convert to grayscale for detection
            gray_davis = cv2.cvtColor(davis_cv_image, cv2.COLOR_BGR2GRAY)
            gray_zed = cv2.cvtColor(zed_cv_image, cv2.COLOR_BGR2GRAY)

            # Find the circle grid in both images
            # Use cv2.CALIB_CB_SYMMETRIC_GRID for symmetric grid
            # Use cv2.CALIB_CB_ASYMMETRIC_GRID for asymmetric grid
            # Check OpenCV docs for specific flags if needed (e.g., adaptiveThreshold, normalization)
            ret1, corners1 = cv2.findCirclesGrid(gray_davis, (NUM_COLS, NUM_ROWS), None, cv2.CALIB_CB_SYMMETRIC_GRID)
            ret2, corners2 = cv2.findCirclesGrid(gray_zed, (NUM_COLS, NUM_ROWS), None, cv2.CALIB_CB_SYMMETRIC_GRID)

            # --- Display Preview with Detection Results ---
            display_davis = davis_cv_image.copy()
            display_zed = zed_cv_image.copy()

            if ret1:
                cv2.drawChessboardCorners(display_davis, (NUM_COLS, NUM_ROWS), corners1, ret1)
                cv2.putText(display_davis, "Pattern Found", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                 cv2.putText(display_davis, "Pattern NOT Found", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if ret2:
                cv2.drawChessboardCorners(display_zed, (NUM_COLS, NUM_ROWS), corners2, ret2)
                cv2.putText(display_zed, "Pattern Found", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                 cv2.putText(display_zed, "Pattern NOT Found", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.imshow("DAVIS View", display_davis)
            cv2.imshow("ZED Left View", display_zed)

            # --- Collect Data if Pattern Found in BOTH Images ---
            key = cv2.waitKey(1) & 0xFF # Check for key press while displaying

            if key == ord('c'): # Press 'c' to trigger data collection for this view
                if ret1 and ret2:
                    print(f"View {len(objectPoints_list) + 1}/{TARGET_CALIBRATION_VIEWS}: Pattern found in BOTH cameras. Collecting data.")

                    # Refine corner locations (optional but recommended)
                    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                    cv2.cornerSubPix(gray_davis, corners1, (11, 11), (-1, -1), criteria)
                    cv2.cornerSubPix(gray_zed, corners2, (11, 11), (-1, -1), criteria)

                    # Append data to the lists
                    objectPoints_list.append(objp)
                    imagePoints1_list.append(corners1) # DAVIS points
                    imagePoints2_list.append(corners2) # ZED points

                    print(f"Collected {len(objectPoints_list)} views so far.")
                    # Add a small delay after collecting to avoid accidental double-capture
                    time.sleep(0.5)

                else:
                     print("Pattern not found in both images. Not collecting data for this view.")

            elif key == ord('q'): # 'q' key to quit
                print("Quitting capture loop.")
                break

        elif err_zed_grab != sl.ERROR_CODE.SUCCESS:
            # Handle ZED grab errors
            print(f"ZED grab failed: {err_zed_grab}")
            time.sleep(0.01) # Wait a bit before trying again

        # If davis_frame is None, it means no new frame was available from DAVIS this iteration.
        # The loop will continue, trying to grab again.

        # Add a short sleep to avoid hogging CPU, adjust as needed
        time.sleep(0.001) # Sleep briefly


    # --- Cleanup ---
    print("\nCapture loop finished.")
    zed.close()
    # Add your DAVIS cleanup code here
    if davis_camera:
        # davis_camera.stop_streaming() # Example cleanup
        pass # dv_processing CameraCapture might handle cleanup on object deletion

    cv2.destroyAllWindows()

    # --- Final Check and Stereo Calibration ---
    if len(objectPoints_list) >= TARGET_CALIBRATION_VIEWS:
        print(f"\nSuccessfully collected data from {len(objectPoints_list)} image pairs.")
        print("objectPoints_list, imagePoints1_list, and imagePoints2_list are ready.")

        # --- Now you can call cv2.stereoCalibrate ---
        # Ensure you have your intrinsic parameters loaded correctly:
        # davis_camera_matrix, davis_dist_coeffs
        # zed_camera_matrix, zed_dist_coeffs
        # And the consistent imageSize_for_stereo

        print("\nCalling cv2.stereoCalibrate...")
        # Flags: cv2.CALIB_FIX_INTRINSIC is common if intrinsics are already good
        # cv2.CALIB_USE_INTRINSIC_GUESS if you want to refine them
        flags = cv2.CALIB_FIX_INTRINSIC
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        try:
            ret, CM1_opt, DC1_opt, CM2_opt, DC2_opt, R, T, E, F = cv2.stereoCalibrate(
                objectPoints_list,
                imagePoints1_list, # DAVIS 2D points
                imagePoints2_list, # ZED Left 2D points
                davis_camera_matrix, davis_dist_coeffs,
                zed_camera_matrix, zed_dist_coeffs,
                imageSize_for_stereo,
                flags=flags, criteria=criteria)

            print("\nStereo calibration successful!")
            print(f"Overall Reprojection Error: {ret}") # Lower is better
            print("Rotation Matrix (R) from DAVIS to ZED Left (3x3):\n", R)
            print("Translation Vector (T) from DAVIS to ZED Left (3x1):\n", T)
            # T is in the same units as your spacing_mm (millimeters in this case)

            # E and F are also computed, representing the epipolar geometry
            # print("\nEssential Matrix (E):\n", E)
            # print("\nFundamental Matrix (F):\n", F)

            if not (flags & cv2.CALIB_FIX_INTRINSIC):
                print("\nRefined Camera Matrix 1 (DAVIS):\n", CM1_opt)
                print("\nRefined Distortion Coefficients 1 (DAVIS):\n", DC1_opt)
                print("\nRefined Camera Matrix 2 (ZED Left):\n", CM2_opt)
                print("\nRefined Distortion Coefficients 2 (ZED Left):\n", DC2_opt)


            # --- Save Calibration Results ---
            print("\nSaving calibration results to stereo_calibration.npz")
            np.savez("stereo_calibration.npz", R=R, T=T, E=E, F=F,
                     cameraMatrix1=davis_camera_matrix, distCoeffs1=davis_dist_coeffs,
                     cameraMatrix2=zed_camera_matrix, distCoeffs2=zed_dist_coeffs,
                     imageSize=imageSize_for_stereo)
            print("Results saved.")


        except Exception as e:
            print(f"\nError during cv2.stereoCalibrate: {e}")
            print("Stereo calibration failed.")


    else:
        print(f"\nDid not collect enough successful image pairs ({len(objectPoints_list)}/{TARGET_CALIBRATION_VIEWS}).")
        print("Stereo calibration was not performed.")

if __name__ == "__main__":
    run()
