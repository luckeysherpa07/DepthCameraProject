import dv_processing as dv
import cv2 as cv
from datetime import timedelta
import os

def run():
    # Open the camera, just use first detected DAVIS camera
    camera = dv.io.CameraCapture("", dv.io.CameraCapture.CameraType.DAVIS)

    # Initialize a multi-stream slicer
    slicer = dv.EventMultiStreamSlicer("events")

    # Add a frame stream to the slicer
    slicer.addFrameStream("frames")

    # Initialize a visualizer for the overlay
    visualizer = dv.visualization.EventVisualizer(
        camera.getEventResolution(),
        dv.visualization.colors.white(),
        dv.visualization.colors.green(),
        dv.visualization.colors.red()
    )

    # Create a window for image display
    cv.namedWindow("Preview", cv.WINDOW_NORMAL)

    # Create output directory
    output_dir = "captured_davis_video"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize video writer (for saving the video)
    video_writer = None
    recording = False

    # Callback method for time-based slicing
    def display_preview(data):
        nonlocal recording, video_writer

        # Retrieve frame data
        frames = data.getFrames("frames")

        # Retrieve event data
        events = data.getEvents("events")

        # Retrieve and color convert the latest frame
        latest_image = None
        if len(frames) > 0:
            if len(frames[-1].image.shape) == 3:
                latest_image = frames[-1].image
            else:
                latest_image = cv.cvtColor(frames[-1].image, cv.COLOR_GRAY2BGR)
        else:
            return

        # Show the preview
        cv.imshow("Preview", visualizer.generateImage(events, latest_image))

        # If recording, write the frame to video file
        if recording and latest_image is not None:
            if video_writer is None:
                # Initialize video writer once the spacebar is pressed
                fourcc = cv.VideoWriter_fourcc(*'XVID')  # Video codec
                filename = os.path.join(output_dir, "recording.avi")
                video_writer = cv.VideoWriter(filename, fourcc, 30.0, (latest_image.shape[1], latest_image.shape[0]))

            video_writer.write(latest_image)

        # Check for keyboard events (Spacebar for recording toggle, ESC to quit)
        key = cv.waitKey(1) & 0xFF
        if key == 27:  # ESC key to exit
            if video_writer:
                video_writer.release()  # Release the video writer if open
            exit(0)
        elif key == 32:  # Spacebar to start/stop recording
            if recording:
                print("Stopping recording.")
                video_writer.release()  # Stop recording
            else:
                print("Starting recording.")
                video_writer = None  # Reset writer to reinitialize it
            recording = not recording

    # Register a job every 40ms
    slicer.doEveryTimeInterval(timedelta(milliseconds=40), display_preview)

    # Main loop
    while camera.isRunning():
        events = camera.getNextEventBatch()
        if events is not None:
            slicer.accept("events", events)

        frame = camera.getNextFrame()
        if frame is not None:
            slicer.accept("frames", [frame])


if __name__ == "__main__":
    run()
