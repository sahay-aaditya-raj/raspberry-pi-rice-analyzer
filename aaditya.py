import cv2
import numpy as np
import csv  # Import the csv module

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
    
    # Convert to HSV for processing 
    hsv = cv2.cvtColor(original_image,cv2.COLOR_BGR2HSV)

    # Convert to grayscale for processing
    grayscale_image = cv2.cvtColor(hsv, cv2.COLOR_BGR2GRAY)
    
    # Thresholding to create a binary image
    _, binary_image = cv2.threshold(
        grayscale_image, 0, 255, 
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Morphological operations to clean the image
    morphological_kernel = np.ones((3, 3), np.uint8)
    cleaned_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, morphological_kernel, iterations=2)

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
    broken_grain_count = 0
    chalky_count =0
    yellow_count = 0

    
    # Lists to store full and broken grain contours
    full_contours = []
    broken_contours = []
    
    # Calculate average area of rice grains
    average_rice_area = 250
    
    # Initialize a list to store mean RGB values
    mean_rgb_values = []
    min_rgb_values = []
    
    # Classify grains as full or broken based on shape and size
    for label in unique_markers:
        if label <= 1:  # Skip background and boundary
            continue
        grain_mask = np.zeros(grayscale_image.shape, dtype="uint8")
        grain_mask[markers == label] = 255
        contours, _ = cv2.findContours(grain_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            area = cv2.contourArea(contours[0])
            M = cv2.moments(contours[0])
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                
                # Extract the pixel values in a circle with a radius of 3 pixels
                circle_radius = 3
                circle_mask = np.zeros(original_image.shape[:2], dtype=np.uint8)
                cv2.circle(circle_mask, (cX, cY), circle_radius, 1, -1)  # Create a filled circle mask
                
                # Extract the pixel values from the original image using the mask
                masked_pixels = original_image[circle_mask == 1]
                
                # Calculate the mean RGB value
                if masked_pixels.size > 0:
                    mean_rgb = masked_pixels.mean(axis=0)
                    min_rgb = masked_pixels.min(axis=0)
                    min_rgb_values.append(min_rgb)
                    mean_rgb_values.append(mean_rgb)
                print(min_rgb_values)

            # Extract the pixel values from the original image using the mask
            contour_mask = np.zeros(original_image.shape[:2], dtype=np.uint8)
            cv2.drawContours(contour_mask, contours, -1, 1, thickness=cv2.FILLED)  # Fill the contour
                
            # Extract the pixel values from the original image using the mask
            masked_pixels = original_image[contour_mask == 1]
            # Calculate the mean RGB value
            
            count_above_threshold = np.sum(np.all(masked_pixels >= [230, 200, 200], axis=1))
            if masked_pixels.size > 0:
                B = masked_pixels.tolist()[0]
                G = masked_pixels.tolist()[1]
                R = masked_pixels.tolist()[2]
                # logging.info(f"Pixel values inside contour at ({cX}, {cY}): {masked_pixels.tolist()}")
                print(f"Pixel values inside contour at ({cX}, {cY}): {masked_pixels.tolist()}")
            mean_rgb = masked_pixels.mean(axis=0)
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
            if count_above_threshold>4:
                chalky_count+=1
                cv2.drawContours(visualization_copy, contours, -1, (0, 255, 255), thickness=cv2.FILLED)
            elif eccentricity >= 0.84 and area > 0.4 * average_rice_area:
                full_grain_count += 1 + grain_multiplier
                # full_contours.extend(contours)
                cv2.drawContours(visualization_copy, contours, -1, (0, 255, 0), thickness=cv2.FILLED)
                
            else:
                broken_grain_count += 1 + grain_multiplier
                # broken_contours.extend(contours)
                cv2.drawContours(visualization_copy, contours, -1, (0, 0, 255), thickness=cv2.FILLED)
    
    # Draw contours on the visualization copy
    if full_contours:
        cv2.drawContours(visualization_copy, full_contours, -1, (0, 255, 0), thickness=cv2.FILLED)  # Green for full grains
    elif broken_contours:
        cv2.drawContours(visualization_copy, broken_contours, -1, (0, 0, 255), thickness=cv2.FILLED)  # Red for broken grains
     # Write mean RGB values

    return (
        visualization_copy,
        full_grain_count,
        broken_grain_count,
        average_rice_area,
        chalky_count
    )

if __name__ == "__main__":
    # Load an image (replace 'path_to_image.jpg' with your actual image path)
    original_image = cv2.imread('images/everything1.jpg')
    
    # Call the function to detect and count rice grains
    results = detect_and_count_rice_grains(original_image)
    
    # Unpack the results
    visualization_copy, full_grain_count, broken_grain_count, average_rice_area,chalky_count = results
    
    # Print the results
    print(f"Full grain count: {full_grain_count}")
    print(f"Broken grain count: {broken_grain_count}")
    print(f"Average rice area: {average_rice_area}")
    print(f"chalky count :{chalky_count}")
    
    # Display the image with contours
    cv2.imshow("Rice Grains Detection", visualization_copy)
    cv2.waitKey(0)
    cv2.destroyAllWindows()