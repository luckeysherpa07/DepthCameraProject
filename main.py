from camera_feature import camera_calibration
from camera_feature import display_live_feed
from camera_feature import zed_timestamp_fps_res
from camera_feature import video_playback
from camera_feature import display_body_tracking
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
        "4": video_capture.run,
        "5": zed_timestamp_fps_res.run,
        "6": video_playback.run,  
        "7": display_depth_video.run,
        "8": display_confidence_map.run,
        "9": display_body_tracking.run,
        "10": display_all_features.run 
    }

    while True:
        print("\nChoose a function to run:")
        print("1. Display ZED Camera Calibration")
        print("2. Display ZED Live Feed")
        print("3. Display DAVIS Live Feed")
        print("4. Capture ZED Video")
        print("5. Display ZED Timestamp, FPS And Resolution")
        print("6. Display ZED RGB Playback")
        print("7. Display ZED Depth Video")
        print("8. Display ZED Confidence Map")
        print("9. Display ZED Body Tracking")
        print("10. Display ZED All Features")
        print("0. Exit")

        try:
            choice = input("Enter the number (0-10): ").strip()
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
