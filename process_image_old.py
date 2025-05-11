import cv2
import numpy as np

def detect_and_count_rice_grains(original_image):
    """
    Detects and counts rice grains in an image using watershed segmentation.
    
    Args:
        original_image (numpy array): Input image containing rice grains.
        
    Returns:
        tuple: Processed image, full rice mask, broken rice mask, full grain count, broken grain count, and average rice area.
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
    
    # Create masks for visualization
    full_rice_mask = np.zeros(grayscale_image.shape, dtype='uint8')
    broken_rice_mask = np.zeros(grayscale_image.shape, dtype='uint8')
    
    if full_contours:
        cv2.drawContours(full_rice_mask, full_contours, -1, 255, thickness=cv2.FILLED)
    if broken_contours:
        cv2.drawContours(broken_rice_mask, broken_contours, -1, 255, thickness=cv2.FILLED)

    return (
        visualization_copy,
        full_rice_mask,
        broken_rice_mask,
        full_grain_count,
        broken_grain_count,
        average_rice_area
    )

def detect_stones(image):
    """
    Detects stones in an image using HSV color space filtering.
    
    Args:
        image (numpy array): Input image containing potential stones.
        
    Returns:
        tuple: Stone mask, stone count, and total stone area.
    """
    # Convert to HSV color space for better color segmentation
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define HSV range for stones (typically brownish-gray)
    lower_stone_color = np.array([5, 50, 50])
    upper_stone_color = np.array([25, 255, 200])
    
    # Create binary mask for stones
    stone_mask = cv2.inRange(hsv_image, lower_stone_color, upper_stone_color)
    
    # Morphological operations to clean the mask
    morphological_kernel = np.ones((3, 3), np.uint8)
    cleaned_stone_mask = cv2.morphologyEx(stone_mask, cv2.MORPH_CLOSE, morphological_kernel, iterations=2)
    
    # Create a mask for confirmed stones only
    confirmed_stone_mask = np.zeros_like(stone_mask)
    
    # Find and analyze stone contours
    stone_contours, _ = cv2.findContours(cleaned_stone_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    stone_count = 0
    total_stone_area = 0
    
    for contour in stone_contours:
        area = cv2.contourArea(contour)
        if area > 20:  # Filter small noise
            if len(contour) >= 5:  # Ensure enough points for ellipse fitting
                ellipse = cv2.fitEllipse(contour)
                (center, axes, angle) = ellipse
                major_axis, minor_axis = max(axes), min(axes)
                aspect_ratio = major_axis / minor_axis if minor_axis != 0 else 0
                
                # Validate stone shape using aspect ratio
                if 1.0 <= aspect_ratio <= 2.0:
                    cv2.drawContours(confirmed_stone_mask, [contour], 0, 255, -1)
                    stone_count += 1
                    total_stone_area += area

    return confirmed_stone_mask, stone_count, total_stone_area

def detect_husk(image):
    """
    Detects husk in an image using HSV color space filtering.
    
    Args:
        image (numpy array): Input image containing potential husk.
        
    Returns:
        tuple: Husk mask, husk count, and total husk area.
    """
    # Convert to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define HSV range for husk (light brown/yellowish)
    lower_husk_color = np.array([10, 30, 50])
    upper_husk_color = np.array([30, 180, 220])
    
    # Create binary mask for husk
    husk_mask = cv2.inRange(hsv_image, lower_husk_color, upper_husk_color)
    
    # Morphological operations to clean the mask
    morphological_kernel = np.ones((3, 3), np.uint8)
    cleaned_husk_mask = cv2.morphologyEx(husk_mask, cv2.MORPH_CLOSE, morphological_kernel, iterations=2)
    
    # Find and analyze husk contours
    husk_contours, _ = cv2.findContours(cleaned_husk_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    clean_husk_mask = np.zeros_like(husk_mask)
    husk_count = 0
    total_husk_area = 0
    
    for contour in husk_contours:
        area = cv2.contourArea(contour)
        if area > 20:  # Filter small noise
            x, y, width, height = cv2.boundingRect(contour)
            aspect_ratio = float(width) / height
            
            # Validate husk shape using aspect ratio
            if 0.2 < aspect_ratio < 0.7 or aspect_ratio > 1.5:
                husk_count += 1
                total_husk_area += area
                cv2.drawContours(clean_husk_mask, [contour], -1, 255, -1)

    return clean_husk_mask, husk_count, total_husk_area

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
    _, full_rice_mask, broken_rice_mask, full_grain_count, broken_grain_count, average_rice_area = detect_and_count_rice_grains(input_image)
    
    # Detect stones
    stone_mask, stone_count, stone_area = detect_stones(input_image)
    
    # Detect husk
    husk_mask, husk_count, husk_area = detect_husk(input_image)
    
    # Apply masks to the result image with specific colors
    result_image[full_rice_mask == 255] = [0, 255, 0]    # Green for full rice grains
    result_image[broken_rice_mask == 255] = [0, 0, 255]  # Blue for broken rice grains
    result_image[stone_mask == 255] = [0, 255, 255]      # Yellow for stones
    result_image[husk_mask == 255] = [255, 0, 255]       # Pink for husk
    
    # Adjust full grain count by subtracting overlapping areas
    overlapping_area = stone_area // average_rice_area + husk_area // average_rice_area
    adjusted_full_grain_count = max(0, full_grain_count - overlapping_area)
    
    # Calculate total objects count
    total_objects = adjusted_full_grain_count + broken_grain_count + stone_count + husk_count
    
    return (
        result_image,
        int(total_objects),
        int(adjusted_full_grain_count),
        int(broken_grain_count),
        int(stone_count),
        int(husk_count)
    )

# Test the function
if __name__ == "__main__":
    image_path = '/home/pi/Desktop/raspi-interface/husk.png'  # Replace with your image path
    input_image = cv2.imread(image_path)
    
    if input_image is not None:
        result_image, total_objects, full_grains, broken_grains, stones, husk = process_image(input_image)
        
        print(f"Total objects: {total_objects}")
        print(f"Full grains: {full_grains}")
        print(f"Broken grains: {broken_grains}")
        print(f"Stones: {stones}")
        print(f"Husk: {husk}")
        
        # Display the result
        cv2.imshow('Processed Image', result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Failed to load image")