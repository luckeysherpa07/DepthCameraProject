import cv2
import os

def run():
    relative_path = "./DAVIS_calibration_file/davis_intrinsics.xml"
    file_path = os.path.abspath(relative_path)

    if not os.path.isfile(file_path):
        print(f"File not found at: {file_path}")
        return

    fs = cv2.FileStorage(file_path, cv2.FILE_STORAGE_READ)
    if not fs.isOpened():
        print(f"Failed to open file: {file_path}")
        return

    camera_node = fs.getNode("DAVIS346_00000001")
    camera_matrix = camera_node.getNode("camera_matrix").mat()
    dist_coeffs = camera_node.getNode("distortion_coefficients").mat()
    fs.release()

    print("Camera Matrix:\n", camera_matrix)
    print("\nDistortion Coefficients:\n", dist_coeffs)

if __name__ == "__main__":
    run()
