import multiprocessing
from camera_feature import camera_calibration
from camera_feature import display_live_feed  # ZED live feed
from camera_feature import zed_timestamp_fps_res
from camera_feature import video_playback
from camera_feature import display_body_tracking
from camera_feature import display_depth_video
from camera_feature import display_confidence_map
from camera_feature import video_capture
from camera_feature import display_all_features
from camera_feature import display_davis_feed

def run_both_davis_zed():
    process1 = multiprocessing.Process(target=display_davis_feed.run)
    process2 = multiprocessing.Process(target=display_live_feed.run)  # ZED live feed

    process1.start()
    process2.start()

    process1.join()
    process2.join()

def main():
    options = {
        "1": camera_calibration.run,
        "2": run_both_davis_zed,  # ✅ Run DAVIS + ZED live feed
        "3": display_live_feed.run,
        "4": display_davis_feed.run,
        "5": video_capture.run,
        "6": zed_timestamp_fps_res.run,
        "7": video_playback.run,  
        "8": display_depth_video.run,
        "9": display_confidence_map.run,
        "10": display_body_tracking.run,
        "11": display_all_features.run 
    }

    while True:
        print("\nChoose a function to run:")
        print("1. Display ZED Camera Calibration")
        print("2. Display Both DAVIS and ZED Live Feed")
        print("3. Display ZED Live Feed")
        print("4. Display DAVIS Live Feed")
        print("5. Capture ZED Video")
        print("6. Display ZED Timestamp, FPS And Resolution")
        print("7. Display ZED RGB Playback")
        print("8. Display ZED Depth Video")
        print("9. Display ZED Confidence Map")
        print("10. Display ZED Body Tracking")
        print("11. Display ZED All Features")
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
    multiprocessing.set_start_method("spawn")
    main()
