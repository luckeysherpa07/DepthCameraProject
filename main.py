from camera_feature import camera_calibration
from camera_feature import display_live_feed  # Now option 2
from camera_feature import depth_confidence_playback  # Option 3
from camera_feature import zed_timestamp
from camera_feature import video_playback
from camera_feature import display_body_tracking  # New import for option 6
from camera_feature import capture_fps
from camera_feature import display_depth_video
from camera_feature import display_confidence_map
from camera_feature import video_capture
from camera_feature import align_video

def main():
    while True:
        print("\nChoose a function to run:")
        print("1. Display Camera Calibration")
        print("2. Display Live Feed")
        print("3. Depth and Confidence Playback")
        print("4. Display ZED Timestamp")
        print("5. Playback Video")
        print("6. Display Body Tracking")  # New option 6
        print("7. Display FPS")
        print("8. Display Depth Video")
        print("9. Display Confidence Map")
        print("10. Capture Video")
        print("11. Align Video")
        print("0. Exit")

        choice = input("Enter the number (0-11): ")

        if choice == "1":
            camera_calibration.run()
        elif choice == "2":
            display_live_feed.run()
        elif choice == "3":
            depth_confidence_playback.run()
        elif choice == "4":
            zed_timestamp.run()
        elif choice == "5":
            video_playback.run()
        elif choice == "6":
            display_body_tracking.run()
        elif choice == "7":
            capture_fps.run()
        elif choice == "8":
            display_depth_video.run()
        elif choice == "9":
            display_confidence_map.run()
        elif choice == "10":
            video_capture.run()
        elif choice == "11":
            align_video.run()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
