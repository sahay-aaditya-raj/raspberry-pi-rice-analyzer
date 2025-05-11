import cv2
import numpy as np

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
    broken_25_count = 0
    broken_50_count = 0
    broken_75_count = 0
    broken_grain_count = 0
    percentage_list = {}
    chalky_count =0
    black_count = 0
    yellow_count = 0
    brown_count = 0
    full_contour = []
    broken_contour =[]
    chalky_contour =[]
    black_contour =[]
    yellow_contour =[]
    brown_contour =[]

    # Calculate average area of rice grains
    average_rice_area = 160
    
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

            # Extract the pixel values from the original image using the mask
            contour_mask = np.zeros(original_image.shape[:2], dtype=np.uint8)
            cv2.drawContours(contour_mask, contours, -1, 1, thickness=cv2.FILLED)  # Fill the contour
            
            # Extract the pixel values from the original image using the mask
            masked_pixels = original_image[contour_mask == 1]
            sorted_bgr = masked_pixels[np.lexsort((masked_pixels[:, 2], masked_pixels[:, 1], masked_pixels[:, 0]))]
            masked_pixels = sorted_bgr[5:-5]
            # Calculate the mean RGB value
            
            count_for_chalky = np.sum(np.all(masked_pixels >= [220, 200, 190], axis=1) & (np.abs(masked_pixels[:, 0] - masked_pixels[:, 2]) < 40))
            count_for_black = np.sum(np.all(masked_pixels <= [150, 130, 140], axis=1))
            count_for_yellow = np.sum(
                (np.all(masked_pixels >= [155, 145, 145], axis=1) &
                np.all(masked_pixels <= [200, 180, 180], axis=1)) &
                (np.abs(masked_pixels[:, 0] - masked_pixels[:, 2]) < 30))
            count_for_brown = np.sum(
                    np.all(masked_pixels >= [95, 75, 105], axis=1) &
                    np.all(masked_pixels <= [110, 95, 125], axis=1))
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
            if count_for_chalky>=4:
                chalky_count+=1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (0, 255, 255), thickness=cv2.FILLED)
                chalky_contour.append(contours)
            elif count_for_brown >= 4 :
                brown_count += 1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (0, 128, 255), thickness=cv2.FILLED)   
                brown_contour.append(contours)      
            elif count_for_yellow >= 8:
                yellow_count +=1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (0, 102, 51), thickness=cv2.FILLED)
                yellow_contour.append(contours)
            elif count_for_black >= 8:
                black_count+=1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (10, 10, 10), thickness=cv2.FILLED)
                black_contour.append(contours)
            elif eccentricity >= 0.84 and area > 0.75 * average_rice_area:
                full_grain_count += 1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (0, 255, 0), thickness=cv2.FILLED) 
                full_contour.append(contours)
            else:
                broken_grain_count += 1 + grain_multiplier
                area_ratio = area / average_rice_area
                brown_contour.append(contours)
                if area_ratio > 0.45:
                    broken_25_count += 1
                    cv2.drawContours(visualization_copy, contours, -1, (0, 0, 255), thickness=cv2.FILLED)
                elif area_ratio > 0.3:
                    broken_50_count += 1
                    cv2.drawContours(visualization_copy, contours, -1, (0, 0, 255), thickness=cv2.FILLED)
                else:
                    broken_75_count += 1
                    cv2.drawContours(visualization_copy, contours, -1, (0, 0, 255), thickness=cv2.FILLED)
            percentage_list = {
                '25%': broken_25_count,
                '50%': broken_50_count,
                '75%': broken_75_count
            }
                
    
    return (
        visualization_copy,
        full_grain_count,
        broken_grain_count,
        chalky_count,
        black_count,
        yellow_count,
        brown_count,
        percentage_list,
        full_contour,
        broken_contour,
        yellow_contour,
        black_contour,
        brown_contour,
        chalky_contour
    )


def detect_stones(image):
    """
    Detects stones in an image using HSV color space filtering and applies a dark blue mask.

    Args:
        image (numpy array): Input image containing potential stones.

    Returns:
        tuple: Image with stones highlighted in dark blue, stone count, and total stone area.
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_stone_color = np.array([5, 50, 50])
    upper_stone_color = np.array([25, 255, 200])
    stone_mask = cv2.inRange(hsv_image, lower_stone_color, upper_stone_color)
    morphological_kernel = np.ones((3, 3), np.uint8)
    cleaned_stone_mask = cv2.morphologyEx(stone_mask, cv2.MORPH_CLOSE, morphological_kernel, iterations=2)
    stone_contours, _ = cv2.findContours(cleaned_stone_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    stone_count = 0
    total_stone_area = 0
    result_image = image.copy()

    for contour in stone_contours:
        area = cv2.contourArea(contour)
        if area > 20:
            if len(contour) >= 5:
                ellipse = cv2.fitEllipse(contour)
                (center, axes, angle) = ellipse
                major_axis, minor_axis = max(axes), min(axes)
                aspect_ratio = major_axis / minor_axis if minor_axis != 0 else 0
                if 1.0 <= aspect_ratio <= 2.0:
                    stone_count += 1
                    total_stone_area += area
                    mask = np.zeros(image.shape[:2], dtype=np.uint8)
                    cv2.drawContours(mask, [contour], 0, 255, thickness=cv2.FILLED)
                    # Use a larger kernel and more iterations for stronger dilation
                    dilated_mask = cv2.dilate(mask, np.ones((7, 7), np.uint8), iterations=2)
                    result_image[dilated_mask == 255] = (139, 0, 0)



    return result_image, stone_count, total_stone_area

def detect_husk(image):
    """
    Detects husk in an image using HSV color space filtering and applies a dark blue mask.

    Args:
        image (numpy array): Input image containing potential husk.

    Returns:
        tuple: Image with husk highlighted in dark blue, binary mask of husks,
               number of detected husks, and total husk area.
    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_husk_color = np.array([0, 10, 30])
    upper_husk_color = np.array([40, 255, 255])
    husk_mask = cv2.inRange(hsv_image, lower_husk_color, upper_husk_color)

    # Morphological operation to clean up the mask
    morphological_kernel = np.ones((3, 3), np.uint8)
    cleaned_husk_mask = cv2.morphologyEx(husk_mask, cv2.MORPH_CLOSE, morphological_kernel, iterations=2)

    # Find contours
    husk_contours, _ = cv2.findContours(cleaned_husk_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    husk_count = 0
    total_husk_area = 0
    result_image = image.copy()
    mask_output = np.zeros(image.shape[:2], dtype=np.uint8)

    husk_contours_return =[]

    for contour in husk_contours:
        area = cv2.contourArea(contour)
        if area > 10:
            x, y, width, height = cv2.boundingRect(contour)
            aspect_ratio = float(width) / height
            if 0.2 < aspect_ratio < 5.0:
                husk_contours_return.append(contour)
                husk_count += 1
                total_husk_area += area
                cv2.drawContours(mask_output, [contour], -1, 255, thickness=cv2.FILLED)
                # Highlight husks in result image
                dilated_mask = cv2.dilate(mask_output, np.ones((7, 7), np.uint8), iterations=2)
                result_image[dilated_mask == 255] = (220,7,13)

    return result_image, husk_count, husk_contours_return

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

    stone_image, stone_count, stone_area = detect_stones(input_image)
    husk_image, husk_count, husk_contours_return = detect_husk(input_image)

    # Detect rice grains
    visual, full_grain_count, broken_grain_count, chalky_count, black_count, yellow_count, brown_count, percent_list, full_contour, broken_contour, yellow_contour, black_contour, brown_contour, chalky_contour = detect_and_count_rice_grains(husk_image)

    # Draw husk contours on the visual image in pink
    cv2.drawContours(visual, husk_contours_return, -1, (255, 192, 203), thickness=cv2.FILLED)  # Pink color

    return (
        visual,
        int(full_grain_count),
        int(chalky_count),
        int(black_count),
        int(yellow_count),
        int(brown_count),
        percent_list,
        int(broken_grain_count),
        int(stone_count),
        int(husk_count),
    )

# Test the function
if __name__ == "__main__":
    image_path = 'images/with_husk.jpg'  # Replace with your image path
    input_image = cv2.imread(image_path)
    
    if input_image is not None:
        visual,full_grain_count, chalky_count, black_count, yellow_count, brown_count, percent_list, broken_grain_count, stone_count, husk_count = process_image(input_image)

    # Print the returned values
        print("Result Image:", visual)
        print("Full Grain Count:", full_grain_count)
        print("Chalky Count:", chalky_count)
        print("Black Count:", black_count)
        print("Yellow Count:", yellow_count)
        print("Brown Count:", brown_count)
        print("Percent List:", percent_list)
        print("Broken Grain Count:", broken_grain_count)
        print("Stone Count:", stone_count)
        print("Husk Count:", husk_count)
        
        # Display the result
        cv2.imshow('Final image :', visual)
        # cv2.imshow('After husk and stone ', result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Failed to load image")