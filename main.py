import camera_calibration
# import rgb_depth_registration
# import zed_timestamp
# import video_capture
import video_playback
# import capture_fps


def main():
    print("Choose a function to run:")
    print("1. Camera Calibration")
    print("2. RGB-Depth Registration")
    # choice = input("Enter the number (1/2): ")

    # camera_calibration.run()
    # rgb_depth_registration.run()
    # zed_timestamp.run()
    # video_capture.run()
    video_playback.run()
    # capture_fps.run()

if __name__ == "__main__":
    main()
