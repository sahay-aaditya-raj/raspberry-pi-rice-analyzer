import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_and_count_rice_grains(image_path, display_results=True):
    """
    Detects and counts rice grains using advanced image processing techniques.
    Handles overlapping grains using watershed segmentation.
    
    Args:
        image_path (str): Path to the input image
        display_results (bool): Whether to display processing steps and results
        
    Returns:
        tuple: (original image, processed image with contours, grain count)
    """
    # Read the image
    original = cv2.imread(image_path)
    if original is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    # Create a copy for visualization
    image_with_contours = original.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    # blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 21, 4
    )
    # Thresholding
    ret, binary = cv2.threshold(
    gray, 0, 255, 
    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Invert the binary image
    binary = cv2.bitwise_not(binary)
    mask = binary == 255
    # newImg = original.copy()
    # green_overlay = np.zeros_like(newImg)
    # green_overlay[mask] = [0, 255, 0]
    # rees = np.where(mask[...,None], green_overlay,newImg)
    # Apply morphological operations to clean the image
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
    # opening = cv2.erode(binary, kernel, iterations=1)
    
    # Perform sure background area extraction
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    
    # Compute the distance transform
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    
    # Normalize the distance transform for better visualization and thresholding
    cv2.normalize(dist_transform, dist_transform, 0, 1.0, cv2.NORM_MINMAX)
    
    # Threshold the distance transform for sure foreground area
    _, sure_fg = cv2.threshold(dist_transform, 0.3 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    
    # Find unknown region (boundary region)
    unknown = cv2.subtract(sure_bg, sure_fg)
    
    # Label the foreground regions
    _, markers = cv2.connectedComponents(sure_fg)
    
    # Add 1 to all labels so that background is not 0, but 1
    markers = markers + 1
    
    # Mark the unknown region with 0
    markers[unknown == 255] = 0
    
    # Apply watershed segmentation
    markers = cv2.watershed(original, markers)
    
    # Count unique regions (excluding background and boundaries)
    unique_markers = np.unique(markers)
    grain_count = len(unique_markers) - 2  # Subtract background and boundary
    
    # Draw contours on the original image
    for label in unique_markers:
        if label <= 1:  # Skip background and boundary
            continue
            
        mask = np.zeros(gray.shape, dtype="uint8")
        mask[markers == label] = 255
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # # Calculate area of the contour
        area = cv2.contourArea(contours[0])
        
        # Filter by area to eliminate noise (tune these values based on your images)
        min_grain_area = 100   # Minimum area for a rice grain
        max_grain_area = 5000  # Maximum area for a rice grain
        
        if min_grain_area <= area <= max_grain_area:
            cv2.drawContours(image_with_contours, contours, -1, (0, 255, 0), 2)
        else:
            grain_count -= 1  # Decrement count if the contour is likely not a grain
        
        
    
    # Display results if requested
    if display_results:
        plt.figure(figsize=(15, 12))
        
        plt.subplot(2, 3, 1)
        plt.imshow(cv2.cvtColor(gray, cv2.COLOR_BGR2RGB))
        plt.title('Original Image')
        
        plt.subplot(2, 3, 2)
        plt.imshow(gray, cmap='gray')
        plt.title('Grayscale')
        
        plt.subplot(2, 3, 3)
        plt.imshow(binary, cmap='gray')
        plt.title('Binary (After Thresholding)')
        
        plt.subplot(2, 3, 4)
        plt.imshow(dist_transform, cmap='jet')
        plt.title('Distance Transform')
        
        plt.subplot(2, 3, 5)
        # Create a colored version of markers for better visualization
        markers_display = np.zeros((markers.shape[0], markers.shape[1], 3), dtype=np.uint8)
        for i in range(2, len(unique_markers)):
            markers_display[markers == unique_markers[i]] = [
                np.random.randint(0, 255),
                np.random.randint(0, 255),
                np.random.randint(0, 255)
            ]
        plt.imshow(markers_display)
        plt.title('Watershed Segmentation')
        
        plt.subplot(2, 3, 6)
        plt.imshow(image_with_contours)
        plt.title(f'Detected Grains: {grain_count}')
        
        plt.tight_layout()
        plt.show()
    
    return original, image_with_contours, grain_count


if __name__ == "__main__":
    # Replace with your image path
    image_path = f"newimgs/a7.jpg"
    original, result, count = detect_and_count_rice_grains(image_path)
    print(f"Detected {count} rice grains using watershed method")
    cv2.imwrite("result_rice_grains.jpg", result)