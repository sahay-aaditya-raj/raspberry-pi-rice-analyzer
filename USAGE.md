# Application Usage Guide

This guide explains how to use the Rice & Dal Analyzer's web interface. Once the application is running, you can access it from any device on the same network as your Raspberry Pi.

## Main Interface

The main interface is divided into two panels:

- **Left Panel**: Contains controls for capturing images, running analysis, and viewing results.
- **Right Panel**: Displays the live camera feed and captured/processed images.

### Controls

- **Capture Image**: Captures a still image from the live camera feed.
- **Retake Image**: If you are not satisfied with the captured image, this button discards it and returns to the live feed.
- **Analyze Rice**: Processes the captured image to identify and count different types of rice grains.
- **Analyze Dal**: Processes the captured image to analyze dal quality.
- **Save Results**: Saves the accumulated analysis results to a local JSON file and attempts to sync with MongoDB.
- **Reset Batch**: Clears the current analysis results.

### Results Display

Analysis results are displayed in real-time in the **Results** section of the left panel. The results are cumulative, meaning each analysis adds to the totals until you reset the batch or save the results.

## Workflow

1. **Position the Grains**: Place a sample of rice or dal under the camera.
2. **Capture**: Click **Capture Image** to take a photo.
3. **Analyze**: Click **Analyze Rice** or **Analyze Dal** depending on the sample.
4. **Review**: The processed image will appear in the right panel, with detected grains outlined. The counts will update in the left panel.
5. **Repeat**: You can capture and analyze multiple images to build a larger sample size. The results will be added together.
6. **Save**: Once you are finished with a batch, click **Save Results**.

---

Next, learn about the image processing techniques used in the [**Image Analysis Explained (`ANALYSIS.md`)**](./ANALYSIS.md) guide.
