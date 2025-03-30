import pyzed.sl as sl

# Function to convert nanoseconds to hours, minutes, and seconds
def convert_to_hms(timestamp_ns):
    timestamp_s = timestamp_ns / 1e9  # Convert nanoseconds to seconds
    hours = int(timestamp_s // 3600)
    minutes = int((timestamp_s % 3600) // 60)
    seconds = int(timestamp_s % 60)
    return hours, minutes, seconds

def run():
    # Set SVO path for playback
    input_path = "output.svo2"  # Change this to your actual file path
    init_parameters = sl.InitParameters()
    init_parameters.set_from_svo_file(input_path)

    # Initialize the ZED camera for playback
    zed = sl.Camera()
    if zed.open(init_parameters) != sl.ERROR_CODE.SUCCESS:
        print("Failed to open SVO file.")
        return

    # Variables to store timestamps
    first_frame_timestamp = None
    last_frame_timestamp = None

    # Grab the first frame (to get the starting timestamp)
    if zed.grab() == sl.ERROR_CODE.SUCCESS:
        first_frame_timestamp = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_nanoseconds()
        first_hms = convert_to_hms(first_frame_timestamp)
        print(f"Starting timestamp: {first_hms[0]:02}:{first_hms[1]:02}:{first_hms[2]:02}")

    # Loop through the SVO file to get the last frame's timestamp
    while zed.grab() == sl.ERROR_CODE.SUCCESS:
        last_frame_timestamp = zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_nanoseconds()

    # Close the ZED camera
    zed.close()

    # Print the last frame's timestamp
    if last_frame_timestamp:
        last_hms = convert_to_hms(last_frame_timestamp)
        print(f"Ending timestamp: {last_hms[0]:02}:{last_hms[1]:02}:{last_hms[2]:02}")

if __name__ == "__main__":
    run()