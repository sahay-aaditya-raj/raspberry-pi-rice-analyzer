import cv2
import numpy as np
import logging
import os

logging.basicConfig(
    filename='rice_grain_detection_full.log',  # Name of the log file
    filemode='a',  # Append mode
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Format of the log messages
)

def detect_and_count_rice_grains(original_image):
    """
    Detects and counts rice grains in an image using watershed segmentation.
    
    Args:
        original_image (numpy array): Input image containing rice grains.
        
    Returns:
        tuple: Processed image, full grain count, broken grain count, and average rice area.
    """
    if original_image is None:
        raise ValueError("Could not read image")
    
    # Create a copy of the original image for visualization
    visualization_copy = original_image.copy()
    
    # Convert to grayscale for processing
    grayscale_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    
    # Thresholding to create a binary image
    _, binary_image = cv2.threshold(
        grayscale_image, 0, 255, 
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Invert the binary image to highlight rice grains
    inverted_binary = cv2.bitwise_not(binary_image)
    
    # Morphological operations to clean the image
    morphological_kernel = np.ones((3, 3), np.uint8)
    cleaned_image = cv2.morphologyEx(inverted_binary, cv2.MORPH_OPEN, morphological_kernel, iterations=2)
    
    cv2.imshow("clean image : ",cleaned_image)
    # Background extraction
    background = cv2.dilate(cleaned_image, morphological_kernel, iterations=3)
    
    # Distance transform for watershed preparation
    distance_transform = cv2.distanceTransform(cleaned_image, cv2.DIST_L2, 5)
    cv2.normalize(distance_transform, distance_transform, 0, 1.0, cv2.NORM_MINMAX)
    
    # Foreground detection
    _, foreground = cv2.threshold(distance_transform, 0.3 * distance_transform.max(), 255, 0)
    foreground = np.uint8(foreground)
    
    # Unknown region identification
    unknown_region = cv2.subtract(background, foreground)
    
    # Connected components labeling
    _, markers = cv2.connectedComponents(foreground)
    markers += 1  # Ensure background is not 0
    markers[unknown_region == 255] = 0
    
    # Watershed segmentation
    markers = cv2.watershed(original_image, markers)
    
    # Count unique regions (excluding background and boundaries)
    unique_markers = np.unique(markers)
    total_grain_count = len(unique_markers) - 2  # Subtract background and boundary
    
    # Initialize counters and storage for full and broken grains
    full_grain_count = 0
    broken_grain_count_25 = 0
    broken_grain_count_50 = 0
    broken_grain_count_75 = 0
    total_area = 0
    valid_contour_count = 0
    
    # Lists to store full and broken grain contours
    full_contours = []
    broken_contours = []
    
    
    # Calculate average area of rice grains
    average_rice_area = 250
    
    # Classify grains as full or broken based on shape and size
    for label in unique_markers:
        if label <= 1:  # Skip background and boundary
            continue
        grain_mask = np.zeros(grayscale_image.shape, dtype="uint8")
        grain_mask[markers == label] = 255
        contours, _ = cv2.findContours(grain_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            area = cv2.contourArea(contours[0])
            try:
                # Calculate eccentricity for shape analysis
                (center, (major_axis, minor_axis), angle) = cv2.fitEllipse(contours[0])
                major = max(major_axis, minor_axis)
                minor = min(major_axis, minor_axis)
                eccentricity = np.sqrt(1 - (minor)**2 / (major)**2)
            except:
                eccentricity = 0
            
            # Handle overlapping or clustered grains
            grain_multiplier = 0
            if area > 2 * average_rice_area:
                grain_multiplier = area // average_rice_area - 1
                total_grain_count += grain_multiplier
            # Classify as full or broken grain
            
            if eccentricity >= 0.84 and area > 0.8 * average_rice_area:
                full_grain_count += 1 + grain_multiplier
                full_contours.extend(contours)
            elif area<= 0.25*average_rice_area:
                broken_grain_count_75 += 1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (0, 0, 255), thickness=cv2.FILLED)
            elif area <= 0.5 * average_rice_area:
                broken_grain_count_50 += 1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (0, 250, 255), thickness=cv2.FILLED)
            else:
                broken_grain_count_25 += 1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (200, 0, 255), thickness=cv2.FILLED)
    
    # Draw contours on the visualization copy
    if full_contours:
        cv2.drawContours(visualization_copy, full_contours, -1, (0, 255, 0), thickness=cv2.FILLED)  # Green for full grains
    if broken_contours:
        cv2.drawContours(visualization_copy, broken_contours, -1, (0, 0, 255), thickness=cv2.FILLED)  # Red for broken grains

    return (
        visualization_copy,
        full_grain_count,
        broken_grain_count_25,
        broken_grain_count_50,
        broken_grain_count_75,
        average_rice_area
    )

if __name__ == "__main__":
    # Specify the directory containing the images
    image_directory = 'images/'  # Adjust this path to your images folder

    # Loop through all files in the directory
    for filename in os.listdir(image_directory):
        # Check if the file is an image (you can add more extensions if needed)
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            # Construct the full file path
            image_path = os.path.join(image_directory, filename)
            
            # Load the image
            original_image = cv2.imread(image_path)
            
            # Call the function to detect and count rice grains
            results = detect_and_count_rice_grains(original_image)
            
            # Unpack the results
            visualization_copy, full_grain_count,b25,b50,b75, average_rice_area = results
            
            # Print the results for the current image
            print(f"Results for {filename}:")
            print(f"Full grain count: {full_grain_count}")
            print(f"Broken grain count: {b25,b50,b75}")
            print(f"Average rice area: {average_rice_area}")
            print("\n")

            # Optionally, display the image with contours
            cv2.imshow(f"Rice Grains Detection - {filename}", visualization_copy)
            cv2.waitKey(0)  # Wait for a key press to move to the next image

    cv2.destroyAllWindows()  # Close all OpenCV windows after processing