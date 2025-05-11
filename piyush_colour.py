import cv2
import numpy as np


def detect_and_count_rice_grains(original_image):
    """
    Detects and counts rice grains in an image using watershed segmentation and classifies them by color.
    
    Args:
        original_image (numpy array): Input image containing rice grains.
        
    Returns:
        tuple: Processed image, full rice mask, broken rice mask, white rice count, red rice count, 
               yellow rice count, full grain count, broken grain count, and average rice area.
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
    total_area = 0
    valid_contour_count = 0
    
    # Initialize color counters
    white_rice_count = 0
    red_rice_count = 0
    yellow_rice_count = 0
    
    # Lists to store full and broken grain contours
    full_contours = []
    broken_contours = []
    
    # Calculate average area of rice grains
    for label in unique_markers:
        if label <= 1:  # Skip background and boundary
            continue
        grain_mask = np.zeros(grayscale_image.shape, dtype="uint8")
        grain_mask[markers == label] = 255
        contours, _ = cv2.findContours(grain_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            area = cv2.contourArea(contours[0])
            total_area += area
            valid_contour_count += 1
    
    # Calculate average area of rice grains
    average_rice_area = total_area / valid_contour_count if valid_contour_count > 0 else 0
    
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
            if eccentricity >= 0.84 or area > 0.6 * average_rice_area:
                full_grain_count += 1 + grain_multiplier
                full_contours.extend(contours)
            else:
                broken_grain_count += 1 + grain_multiplier
                broken_contours.extend(contours)
    
    # Classify grains by color
    for label in unique_markers:
        if label <= 1:  # Skip background and boundary
            continue
        grain_mask = np.zeros(grayscale_image.shape, dtype="uint8")
        grain_mask[markers == label] = 255
        contours, _ = cv2.findContours(grain_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Create a mask for the current contour
            mask = np.zeros(original_image.shape[:2], dtype="uint8")
            cv2.drawContours(mask, [contours[0]], -1, 255, thickness=cv2.FILLED)
            
            # Extract the region of interest (ROI) from the original image using the mask
            roi = cv2.bitwise_and(original_image, original_image, mask=mask)
            
            # Convert ROI to HSV color space
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Define color ranges
            # White color range
            lower_white = np.array([0, 0, 200])
            upper_white = np.array([180, 30, 255])
            mask_white = cv2.inRange(hsv_roi, lower_white, upper_white)
            white_pixels = np.sum(mask_white == 255)
            
            # Red color range (split into two ranges)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            mask_red1 = cv2.inRange(hsv_roi, lower_red1, upper_red1)
            mask_red2 = cv2.inRange(hsv_roi, lower_red2, upper_red2)
            mask_red = cv2.bitwise_or(mask_red1, mask_red2)
            red_pixels = np.sum(mask_red == 255)
            
            # Yellow color range
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])
            mask_yellow = cv2.inRange(hsv_roi, lower_yellow, upper_yellow)
            yellow_pixels = np.sum(mask_yellow == 255)
            
            # Determine the majority color
            total_pixels = white_pixels + red_pixels + yellow_pixels
            if total_pixels == 0:
                continue  # Skip if no pixels are found
            
            if white_pixels > red_pixels and white_pixels > yellow_pixels:
                white_rice_count += 1
            elif red_pixels > yellow_pixels:
                red_rice_count += 1
            else:
                yellow_rice_count += 1
    
    # Create masks for visualization
    full_rice_mask = np.zeros(grayscale_image.shape, dtype='uint8')
    broken_rice_mask = np.zeros(grayscale_image.shape, dtype='uint8')
    white_rice_mask = np.zeros(grayscale_image.shape, dtype='uint8')
    red_rice_mask = np.zeros(grayscale_image.shape, dtype='uint8')
    yellow_rice_mask = np.zeros(grayscale_image.shape, dtype='uint8')
    
    if full_contours:
        cv2.drawContours(full_rice_mask, full_contours, -1, 255, thickness=cv2.FILLED)
    if broken_contours:
        cv2.drawContours(broken_rice_mask, broken_contours, -1, 255, thickness=cv2.FILLED)
    
    # Draw color masks
    for label in unique_markers:
        if label <= 1:
            continue
        grain_mask = np.zeros(grayscale_image.shape, dtype="uint8")
        grain_mask[markers == label] = 255
        contours, _ = cv2.findContours(grain_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Create a mask for the current contour
            mask = np.zeros(original_image.shape[:2], dtype="uint8")
            cv2.drawContours(mask, [contours[0]], -1, 255, thickness=cv2.FILLED)
            
            # Extract the region of interest (ROI) from the original image using the mask
            roi = cv2.bitwise_and(original_image, original_image, mask=mask)
            
            # Convert ROI to HSV color space
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Define color ranges
            lower_white = np.array([0, 0, 200])
            upper_white = np.array([180, 30, 255])
            mask_white = cv2.inRange(hsv_roi, lower_white, upper_white)
            white_pixels = np.sum(mask_white == 255)
            
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            mask_red1 = cv2.inRange(hsv_roi, lower_red1, upper_red1)
            mask_red2 = cv2.inRange(hsv_roi, lower_red2, upper_red2)
            mask_red = cv2.bitwise_or(mask_red1, mask_red2)
            red_pixels = np.sum(mask_red == 255)
            
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])
            mask_yellow = cv2.inRange(hsv_roi, lower_yellow, upper_yellow)
            yellow_pixels = np.sum(mask_yellow == 255)
            
            # Determine the majority color
            if white_pixels > red_pixels and white_pixels > yellow_pixels:
                cv2.drawContours(white_rice_mask, contours, -1, 255, thickness=cv2.FILLED)
            elif red_pixels > yellow_pixels:
                cv2.drawContours(red_rice_mask, contours, -1, 255, thickness=cv2.FILLED)
            else:
                cv2.drawContours(yellow_rice_mask, contours, -1, 255, thickness=cv2.FILLED)
    
    return (
        visualization_copy,
        full_rice_mask,
        broken_rice_mask,
        white_rice_mask,
        red_rice_mask,
        yellow_rice_mask,
        white_rice_count,
        red_rice_count,
        yellow_rice_count,
        full_grain_count,
        broken_grain_count,
        average_rice_area
    )

def process_image(input_image):
    """
    Processes an image to identify and visualize different components (rice, stones, husk).
    
    Args:
        input_image (numpy array): Input image containing rice and potential impurities.
        
    Returns:
        tuple: Processed image with masks applied, and counts of various components.
    """
    if input_image is None:
        raise ValueError("Could not read image")
    
    # Create a copy of the original image for visualization
    result_image = input_image.copy()
    
    # Detect rice grains
    (visualization_copy, full_rice_mask, broken_rice_mask, white_rice_mask, 
     red_rice_mask, yellow_rice_mask, white_rice_count, red_rice_count, 
     yellow_rice_count, full_grain_count, broken_grain_count, 
     average_rice_area) = detect_and_count_rice_grains(input_image)
    
    # Detect stones using color thresholding
    # Convert to HSV color space
    hsv_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2HSV)
    
    # Stone detection (typically darker regions)
    lower_stone = np.array([0, 0, 0])
    upper_stone = np.array([180, 255, 50])
    stone_mask = cv2.inRange(hsv_image, lower_stone, upper_stone)
    
    # Apply morphological operations to clean the mask
    morphological_kernel = np.ones((5, 5), np.uint8)
    stone_mask = cv2.morphologyEx(stone_mask, cv2.MORPH_OPEN, morphological_kernel, iterations=2)
    stone_mask = cv2.morphologyEx(stone_mask, cv2.MORPH_CLOSE, morphological_kernel, iterations=2)
    
    # Find contours of stones
    stone_contours, _ = cv2.findContours(stone_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter out small contours that are likely noise
    stone_contours = [cnt for cnt in stone_contours if cv2.contourArea(cnt) > average_rice_area * 0.5]
    stone_count = len(stone_contours)
    
    # Detect husk using color thresholding
    # Husk is typically lighter and has different texture
    lower_husk = np.array([0, 0, 150])
    upper_husk = np.array([180, 40, 255])
    husk_mask = cv2.inRange(hsv_image, lower_husk, upper_husk)
    
    # Apply morphological operations to clean the mask
    husk_mask = cv2.morphologyEx(husk_mask, cv2.MORPH_OPEN, morphological_kernel, iterations=2)
    husk_mask = cv2.morphologyEx(husk_mask, cv2.MORPH_CLOSE, morphological_kernel, iterations=2)
    
    # Subtract rice masks to isolate husk
    husk_mask = cv2.bitwise_and(husk_mask, cv2.bitwise_not(full_rice_mask))
    husk_mask = cv2.bitwise_and(husk_mask, cv2.bitwise_not(broken_rice_mask))
    
    # Find contours of husk
    husk_contours, _ = cv2.findContours(husk_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter out small contours that are likely noise
    husk_contours = [cnt for cnt in husk_contours if cv2.contourArea(cnt) > average_rice_area * 0.2]
    husk_count = len(husk_contours)
    
    # Apply masks to the result image with specific colors
    result_image[full_rice_mask == 255] = [0, 255, 0]    # Green for full rice grains
    result_image[broken_rice_mask == 255] = [0, 0, 255]  # Blue for broken rice grains
    result_image[white_rice_mask == 255] = [255, 255, 255]  # White for white rice
    result_image[red_rice_mask == 255] = [0, 0, 128]      # Dark red for red rice
    result_image[yellow_rice_mask == 255] = [0, 255, 255] # Yellow for yellow rice
    result_image[stone_mask == 255] = [128, 0, 0]         # Brown for stones
    result_image[husk_mask == 255] = [128, 128, 128]      # Gray for husk
    
    # Draw contours for stones and husk
    cv2.drawContours(result_image, stone_contours, -1, (128, 0, 0), 2)
    cv2.drawContours(result_image, husk_contours, -1, (128, 128, 128), 2)
    
    return (
        result_image,
        full_grain_count,
        broken_grain_count,
        white_rice_count,
        red_rice_count,
        yellow_rice_count,
        stone_count,
        husk_count
    )

# Test the function
if __name__ == "__main__":
    image_path = '/home/mayasur/Desktop/raspi-interface/static/captured/captured_1743981899.jpg'  # Replace with your image path
    input_image = cv2.imread(image_path)
    
    if input_image is not None:
        result_image, full_grains, broken_grains, white, red, yellow, stones, husk = process_image(input_image)
        
        # print(f"Total objects: {total_objects}")
        print(f"Full grains: {full_grains}")
        print(f"Broken grains: {broken_grains}")
        print(f"White rice: {white}")
        print(f"Red rice: {red}")
        print(f"Yellow rice: {yellow}")
        print(f"Stones: {stones}")
        print(f"Husk: {husk}")
        
        # Display the result
        cv2.imshow('Processed Image', result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Failed to load image")