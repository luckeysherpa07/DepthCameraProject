from camera_feature import camera_calibration
from camera_feature import video_capture
from camera_feature import zed_timestamp
from camera_feature import video_playback
from camera_feature import capture_fps
from camera_feature import display_depth_video
from camera_feature import display_confidence_map
from camera_feature import align_video

def main():
    print("Choose a function to run:")
    print("1. Display Camera Calibration")
    print("2. Capture Video")
    print("3. Display ZED Timestamp")
    print("4. Playback Video")
    print("5. Display Depth Video")
    print("6. Display Confidence Map")
    print("7. Display FPS")
    # print("8. Align Video")

    choice = input("Enter the number (1/2/3/4/5/6/7/8): ")

    if choice == "1":
        camera_calibration.run()
    elif choice == "2":
        video_capture.run()
    elif choice == "3":
        zed_timestamp.run()
    elif choice == "4":
        video_playback.run()
    elif choice == "5":
        display_depth_video.run()
    elif choice == "6":
        display_confidence_map.run()
    elif choice == "7":
        capture_fps.run()
    elif choice == "8":
        align_video.run()
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
