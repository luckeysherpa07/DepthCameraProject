import dv_processing as dv
import cv2 as cv
from datetime import timedelta

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

    # Callback method for time-based slicing
    def display_preview(data):
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

        # Generate and show the overlay image
        cv.imshow("Preview", visualizer.generateImage(events, latest_image))

        # Exit on ESC key
        if cv.waitKey(2) == 27:
            exit(0)

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

# To run the function
if __name__ == "__main__":
    run()
