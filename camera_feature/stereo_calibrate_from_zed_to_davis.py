import pyzed.sl as sl
import numpy as np
import cv2
import os

def run():
    # --- ZED Camera ---
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.sdk_verbose = 0

    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        print("Failed to open ZED camera.")
    else:
        calib = zed.get_camera_information().camera_configuration.calibration_parameters
        left_cam = calib.left_cam

        zed_camera_matrix = np.array([
            [left_cam.fx, 0, left_cam.cx],
            [0, left_cam.fy, left_cam.cy],
            [0, 0, 1]
        ])

        zed_dist_coeffs = np.array(left_cam.disto)

        print("ZED Camera Matrix (Left):\n", zed_camera_matrix)
        print("\nZED Distortion Coefficients (Left):\n", zed_dist_coeffs)

        zed.close()

    # --- DAVIS Camera ---
    relative_path = "./DAVIS_calibration_file/davis_intrinsics.xml"
    file_path = os.path.abspath(relative_path)

    if not os.path.isfile(file_path):
        print(f"\nDAVIS file not found at: {file_path}")
        return

    fs = cv2.FileStorage(file_path, cv2.FILE_STORAGE_READ)
    if not fs.isOpened():
        print(f"\nFailed to open DAVIS file: {file_path}")
        return

    camera_node = fs.getNode("DAVIS346_00000001")
    davis_camera_matrix = camera_node.getNode("camera_matrix").mat()
    davis_dist_coeffs = camera_node.getNode("distortion_coefficients").mat()
    fs.release()

    print("\nDAVIS Camera Matrix:\n", davis_camera_matrix)
    print("\nDAVIS Distortion Coefficients:\n", davis_dist_coeffs)

if __name__ == "__main__":
    run()
