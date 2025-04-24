import multiprocessing
from camera_feature import camera_calibration
from camera_feature import display_live_feed 
from camera_feature import zed_timestamp_fps_res
from camera_feature import video_playback
from camera_feature import display_body_tracking
from camera_feature import display_depth_video
from camera_feature import display_confidence_map
from camera_feature import video_capture
from camera_feature import display_all_features
from camera_feature import display_davis_feed
from camera_feature import display_davis_calibration
from camera_feature import display_davis_playback
from camera_feature import davis_timestamp_fps_res
def run_both_davis_zed():
    process1 = multiprocessing.Process(target=display_davis_feed.run)
    process2 = multiprocessing.Process(target=display_live_feed.run) 

    process1.start()
    process2.start()

    process1.join()
    process2.join()

def main():
    options = {
        "1": camera_calibration.run,
        "2": display_davis_calibration.run, 
        "3": run_both_davis_zed, 
        "4": display_live_feed.run,
        "5": display_davis_feed.run,
        "6": display_davis_playback.run,
        "7": davis_timestamp_fps_res.run,            
        "8": video_capture.run,
        "9": zed_timestamp_fps_res.run,
        "10": video_playback.run,  
        "11": display_depth_video.run,
        "12": display_confidence_map.run,
        "13": display_body_tracking.run,
        "14": display_all_features.run
    }

    while True:
        print("\nChoose a function to run:")
        print("1. Display ZED Camera Calibration Info")
        print("2. Display DAVIS Camera Info")
        print("3. Display Both DAVIS and ZED Live Feed")
        print("4. Display ZED Live Feed")
        print("5. Display DAVIS Live Feed")
        print("6. Display DAVIS Playback")
        print("7. Display DAVIS Timestamp, FPS And Resolution")  
        print("8. Capture ZED Video")                             
        print("9. Display ZED Timestamp, FPS And Resolution")
        print("10. Display ZED RGB Playback")
        print("11. Display ZED Depth Video")
        print("12. Display ZED Confidence Map")
        print("13. Display ZED Body Tracking")
        print("14. Display ZED All Features")
        print("0. Exit")

        try:
            choice = input("Enter the number (0-14): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if choice == "0":
            print("Exiting...")
            break
        elif choice in options:
            print(f"\nRunning option {choice}...\n")
            options[choice]()
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    main()
