import pyzed.sl as sl

def run():
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.sdk_verbose = 0

    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        exit(1)

    calibration_params = zed.get_camera_information().camera_configuration.calibration_parameters
    focal_left_x = calibration_params.left_cam.fx
    focal_left_y = calibration_params.left_cam.fy
    focal_right_x = calibration_params.right_cam.fx
    focal_right_y = calibration_params.right_cam.fy
    k1 = calibration_params.left_cam.disto[0]
    tx = calibration_params.stereo_transform.get_translation().get()[0]
    h_fov = calibration_params.left_cam.h_fov

    print(f"Focal Length (Left X): {focal_left_x}")
    print(f"Focal Length (Left Y): {focal_left_y}")
    print(f"Focal Length (Right X): {focal_right_x}")
    print(f"Focal Length (Right Y): {focal_right_y}")
    print(f"Radial Distortion (k1): {k1}")
    print(f"Translation (tx): {tx}")
    print(f"Horizontal FoV: {h_fov}")

    zed.close()

if __name__ == "__main__":
    run()