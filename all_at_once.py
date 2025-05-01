import cv2
import numpy as np
import os


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
    
    # Calculate average area of rice grains
    average_rice_area = 225
    
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
            elif count_for_brown >= 5 :
                brown_count += 1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (0, 128, 255), thickness=cv2.FILLED)         
            elif count_for_yellow >= 9:
                yellow_count +=1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (0, 102, 51), thickness=cv2.FILLED)
            elif count_for_black >= 7:
                black_count+=1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (10, 10, 10), thickness=cv2.FILLED)
            elif eccentricity >= 0.84 and area > 0.6 * average_rice_area:
                full_grain_count += 1 + grain_multiplier
                cv2.drawContours(visualization_copy, contours, -1, (0, 255, 0), thickness=cv2.FILLED) 
            else:
                broken_grain_count += 1 + grain_multiplier
                area_ratio = area / average_rice_area
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
        percentage_list
    )

if __name__ == "__main__":
    # Define the path to the images folder
    images_folder = 'images'
    
    # Loop through all files in the images folder
    for image_file in os.listdir(images_folder):
        if image_file.endswith(('.jpg', '.jpeg', '.png')):  # Check for image file types
            image_path = os.path.join(images_folder, image_file)
            original_image = cv2.imread(image_path)
            
            # Call the function to detect and count rice grains
            results = detect_and_count_rice_grains(original_image)
            
            visualization_copy, full_grain_count, broken_grain_count, chalky_count, black_count, yellow_count, brown_count, percent_list = results
    
            # Print the results
            print(f"Full grain count: {full_grain_count}")
            print(f"Broken grain count: {broken_grain_count}")
            print(f"chalky count :{chalky_count}")
            print(f"Brown rice count: {brown_count}")
            print(f"yellow rice count :{yellow_count}")
            print(f"black rice count :{black_count}")
            print(f"percent : {percent_list}")
            
            # Display the image with contours
            cv2.imshow(f"Rice Grains Detection - {image_file}", visualization_copy)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

# black is for black
# orange is for brown
# olive is for yellow
# green is full 
# red is broken 
# yellow means chalky