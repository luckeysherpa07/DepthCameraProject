from camera_feature import camera_calibration
from camera_feature import display_live_feed 
from camera_feature import zed_timestamp
from camera_feature import video_playback
from camera_feature import display_body_tracking
from camera_feature import capture_fps
from camera_feature import display_depth_video
from camera_feature import display_confidence_map
from camera_feature import video_capture
from camera_feature import align_video
from camera_feature import display_all_features
from camera_feature import display_davis_feed  # New import

def main():
    while True:
        print("\nChoose a function to run:")
        print("1. Display Camera Calibration")
        print("2. Display Live Feed")
        print("3. Display Live Feed from DAVIS")  # New option
        print("4. Display All Features")
        print("5. Display ZED Timestamp")
        print("6. Playback Video")
        print("7. Display Body Tracking")
        print("8. Display FPS")
        print("9. Display Depth Video")
        print("10. Display Confidence Map")
        print("11. Capture Video")
        print("12. Align Video")
        print("0. Exit")

        choice = input("Enter the number (0-12): ")

        if choice == "1":
            camera_calibration.run()
        elif choice == "2":
            display_live_feed.run()
        elif choice == "3":
            display_davis_feed.run()  # New function
        elif choice == "4":
            display_all_features.run()
        elif choice == "5":
            zed_timestamp.run()
        elif choice == "6":
            video_playback.run()
        elif choice == "7":
            display_body_tracking.run()
        elif choice == "8":
            capture_fps.run()
        elif choice == "9":
            display_depth_video.run()
        elif choice == "10":
            display_confidence_map.run()
        elif choice == "11":
            video_capture.run()
        elif choice == "12":
            align_video.run()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
