from camera_feature import camera_calibration
from camera_feature import display_live_feed 
from camera_feature import zed_timestamp
from camera_feature import video_playback
from camera_feature import display_body_tracking
from camera_feature import capture_fps
from camera_feature import display_depth_video
from camera_feature import display_confidence_map
from camera_feature import video_capture
from camera_feature import display_all_features
from camera_feature import display_davis_feed  # New import

def main():
    options = {
        "1": camera_calibration.run,
        "2": display_live_feed.run,
        "3": display_davis_feed.run,
        "4": display_all_features.run,
        "5": zed_timestamp.run,
        "6": video_playback.run,
        "7": display_body_tracking.run,
        "8": capture_fps.run,
        "9": display_depth_video.run,
        "10": display_confidence_map.run,
        "11": video_capture.run
    }

    while True:
        print("\nChoose a function to run:")
        print("1. Display Camera Calibration")
        print("2. Display Live Feed")
        print("3. Display Live Feed from DAVIS")
        print("4. Display All Features")
        print("5. Display ZED Timestamp")
        print("6. Playback Video")
        print("7. Display Body Tracking")
        print("8. Display FPS")
        print("9. Display Depth Video")
        print("10. Display Confidence Map")
        print("11. Capture Video")
        print("0. Exit")

        try:
            choice = input("Enter the number (0-11): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if choice == "0":
            print("Exiting...")
            break
        elif choice in options:
            options[choice]()
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
