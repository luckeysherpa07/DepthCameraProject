import numpy as np
import cv2
import glob
import os

def run():
    # --- Load known intrinsics ---
    import pyzed.sl as sl
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

    # --- Chessboard pattern settings ---
    num_rows = 4
    num_cols = 5
    spacing_mm = 50.0
    objp = np.zeros((num_rows * num_cols, 3), np.float32)
    objp[:, :2] = np.mgrid[0:num_cols, 0:num_rows].T.reshape(-1, 2) * spacing_mm

    print("\nGenerated Object Points (objp):\n", objp)
    
    # --- Load and process image pairs ---
    images_zed = sorted(glob.glob("zed_left/*.png"))
    images_davis = sorted(glob.glob("davis_right/*.png"))

    objectPoints, imagePoints1, imagePoints2 = [], [], []

    for imgZED_path, imgDAVIS_path in zip(images_zed, images_davis):
        imgZED = cv2.imread(imgZED_path)
        imgDAVIS = cv2.imread(imgDAVIS_path)
        grayZED = cv2.cvtColor(imgZED, cv2.COLOR_BGR2GRAY)
        grayDAVIS = cv2.cvtColor(imgDAVIS, cv2.COLOR_BGR2GRAY)

        foundZED, cornersZED = cv2.findChessboardCorners(grayZED, (num_cols, num_rows), None)
        foundDAVIS, cornersDAVIS = cv2.findChessboardCorners(grayDAVIS, (num_cols, num_rows), None)

        if foundZED and foundDAVIS:
            objectPoints.append(objp.copy())
            imagePoints1.append(cornersZED)
            imagePoints2.append(cornersDAVIS)

    if objectPoints:
        print("\nSample Object Points:\n", objectPoints[0])
    else:
        print("No object points found. Check your pattern detection.")
        return

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)

    ret, _, _, _, _, R, T, E, F = cv2.stereoCalibrate(
        objectPoints,
        imagePoints1,
        imagePoints2,
        zed_camera_matrix, zed_dist_coeffs,
        davis_camera_matrix, davis_dist_coeffs,
        grayZED.shape[::-1],
        flags=cv2.CALIB_FIX_INTRINSIC,
        criteria=criteria
    )

    print("\nRotation Matrix R:\n", R)
    print("\nTranslation Vector T:\n", T)
    print("\nEssential Matrix E:\n", E)
    print("\nFundamental Matrix F:\n", F)

if __name__ == "__main__":
    run()
