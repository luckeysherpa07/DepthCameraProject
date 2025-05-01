import numpy as np
import cv2
import glob
import os
import pyzed.sl as sl

def load_intrinsics():
    # --- ZED Camera ---
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.sdk_verbose = 0
    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        raise Exception("Failed to open ZED camera.")
    calib = zed.get_camera_information().camera_configuration.calibration_parameters
    left_cam = calib.left_cam
    zed_camera_matrix = np.array([
        [left_cam.fx, 0, left_cam.cx],
        [0, left_cam.fy, left_cam.cy],
        [0, 0, 1]
    ])
    zed_dist_coeffs = np.array(left_cam.disto)
    zed.close()

    print("ZED Camera Matrix:\n", zed_camera_matrix)
    print("ZED Distortion Coefficients:\n", zed_dist_coeffs)

    # --- DAVIS Camera ---
    relative_path = "./DAVIS_calibration_file/davis_intrinsics.xml"  
    file_path = os.path.abspath(relative_path)
    fs = cv2.FileStorage(file_path, cv2.FILE_STORAGE_READ)
    if not fs.isOpened():
        raise Exception("Failed to open DAVIS calibration file.")
    camera_node = fs.getNode("DAVIS346_00000001")
    davis_camera_matrix = camera_node.getNode("camera_matrix").mat()
    davis_dist_coeffs = camera_node.getNode("distortion_coefficients").mat()
    fs.release()

    print("\nDAVIS Camera Matrix:\n", davis_camera_matrix)
    print("DAVIS Distortion Coefficients:\n", davis_dist_coeffs)

    return zed_camera_matrix, zed_dist_coeffs, davis_camera_matrix, davis_dist_coeffs

def run():
    # --- Circle grid pattern settings ---
    num_rows = 4
    num_cols = 5
    spacing_mm = 50.0
    pattern_size = (num_cols, num_rows)  # columns x rows

    objp = np.zeros((num_rows * num_cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:num_cols, 0:num_rows].T.reshape(-1, 2) * spacing_mm

    print("\nObject Points:\n", objp)

    # --- Load image pairs ---
    zed_images = sorted(glob.glob("./ZED_calibration_images/*.png"))  
    davis_images = sorted(glob.glob("./DAVIS_calibration_images/*.png"))

    objectPoints, imagePoints_zed, imagePoints_davis = [], [], []

    for zed_path, davis_path in zip(zed_images, davis_images):
        img_zed = cv2.imread(zed_path)
        img_davis = cv2.imread(davis_path)
        gray_zed = cv2.cvtColor(img_zed, cv2.COLOR_BGR2GRAY)
        gray_davis = cv2.cvtColor(img_davis, cv2.COLOR_BGR2GRAY)

        found_zed, corners_zed = cv2.findCirclesGrid(gray_zed, pattern_size, flags=cv2.CALIB_CB_SYMMETRIC_GRID)
        found_davis, corners_davis = cv2.findCirclesGrid(gray_davis, pattern_size, flags=cv2.CALIB_CB_SYMMETRIC_GRID)

        if found_zed and found_davis:
            objectPoints.append(objp.copy())
            imagePoints_zed.append(corners_zed)
            imagePoints_davis.append(corners_davis)

    if not objectPoints:
        print("No valid pattern pairs found. Check image quality and pattern visibility.")
        return

    # --- Load intrinsics ---
    zed_K, zed_dist, davis_K, davis_dist = load_intrinsics()

    # --- Stereo Calibration ---
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)

    ret, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
        objectPoints,
        imagePoints_zed,
        imagePoints_davis,
        zed_K, zed_dist,
        davis_K, davis_dist,
        gray_zed.shape[::-1],
        flags=cv2.CALIB_FIX_INTRINSIC,
        criteria=criteria
    )

    print("\nStereo Calibration Results:")
    print("Rotation Matrix R:\n", R)
    print("Translation Vector T:\n", T)
    print("Essential Matrix E:\n", E)
    print("Fundamental Matrix F:\n", F)

if __name__ == "__main__":
    run()
