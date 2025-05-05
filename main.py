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
from camera_feature import stereo_calibrate_from_zed_to_davis
from camera_feature import stereo_calibrate_from_dvsense_to_davis  # ✅ New import
from camera_feature import display_extrinsic_parameters
from camera_feature import display_rectified_view
from camera_feature import convert_svo_to_mp4  # New import for SVO to MP4 conversion

def run_both_davis_zed(recording_flag):
    process1 = multiprocessing.Process(target=display_davis_feed.run, args=(recording_flag,))
    process2 = multiprocessing.Process(target=display_live_feed.run, args=(recording_flag,))
    process1.start()
    process2.start()
    process1.join()
    process2.join()

def main():
    recording_flag = multiprocessing.Value('b', False)

    # Functions that require the recording_flag argument
    options_with_args = {
        "3": run_both_davis_zed,  # This requires recording_flag
        "4": display_live_feed.run,  # This requires recording_flag
        "5": display_davis_feed.run,  # This requires recording_flag
        "17": display_rectified_view.run,
    }

    # Functions that do not require arguments
    options = {
        "1": camera_calibration.run,
        "2": display_davis_calibration.run,
        "6": display_davis_playback.run,
        "7": davis_timestamp_fps_res.run,
        "8": video_capture.run,
        "9": zed_timestamp_fps_res.run,
        "10": video_playback.run,
        "11": display_depth_video.run,
        "12": display_confidence_map.run,
        "13": display_body_tracking.run,
        "14": display_all_features.run,
        "15": stereo_calibrate_from_zed_to_davis.run,
        "16": display_extrinsic_parameters.run,
        "18": stereo_calibrate_from_dvsense_to_davis.run,
        "19": convert_svo_to_mp4.run,  # New option for SVO to MP4 conversion
    }

    while True:
        print("\nChoose a function to run:")
        print("1.  Display ZED Camera Calibration Info")
        print("2.  Display DAVIS Camera Info")
        print("3.  Display Both DAVIS and ZED Live Feed")
        print("4.  Display ZED Live Feed")
        print("5.  Display DAVIS Live Feed")
        print("6.  Display DAVIS Playback")
        print("7.  Display DAVIS Timestamp, FPS And Resolution")
        print("8.  Capture ZED Video")
        print("9.  Display ZED Timestamp, FPS And Resolution")
        print("10. Display ZED RGB Playback")
        print("11. Display ZED Depth Video")
        print("12. Display ZED Confidence Map")
        print("13. Display ZED Body Tracking")
        print("14. Display ZED All Features")
        print("15. StereoCalibrate ZED to DAVIS")
        print("16. Display Extrinsic Parameter Info")
        print("17. Display Rectified View from ZED and DAVIS")
        print("18. StereoCalibrate DVSense to DAVIS")
        print("19. Convert SVO to MP4")  # New option
        print("0.  Exit")

        try:
            choice = input("Enter the number (0-19): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if choice == "0":
            print("Exiting...")
            break
        elif choice in options_with_args:
            print(f"\nRunning option {choice}...\n")
            options_with_args[choice](recording_flag)  # Pass the recording_flag here
        elif choice in options:
            print(f"\nRunning option {choice}...\n")
            options[choice]()  # No arguments needed
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    main()
