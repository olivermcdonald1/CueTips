import cv2
import numpy as np

def enhanced_rail_detection(image):
    """
    Detect the inside edges of the pool table rails closest to the felt.
    
    Args:
        image (numpy array): Input image as a numpy array.
    
    Returns:
        list: Detected inside rail edges
    """
    # Convert to grayscale and preprocess
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(gray)
    denoised = cv2.bilateralFilter(equalized, 9, 75, 75)
    edges = cv2.Canny(denoised, 50, 200)

    # Dilate edges
    kernel = np.ones((3, 3), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=2)

    # Detect lines with Hough Transform
    lines = cv2.HoughLinesP(
        dilated_edges,
        rho=1,
        theta=np.pi / 180,
        threshold=80,  # Higher threshold for more robust detection
        minLineLength=50,
        maxLineGap=15
    )

    rail_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            if length > 100 and (angle < 15 or 75 < angle < 105 or angle > 165):
                rail_lines.append((x1, y1, x2, y2))

    return rail_lines

def get_inside_table_edges(rail_lines):
    """
    Extract the four main inside edges (top, bottom, left, right) of the pool table.
    
    Args:
        rail_lines (list): Detected rail lines.
    
    Returns:
        list: Coordinates of the four edges in (x1, y1, x2, y2) format.
    """
    # Separate horizontal and vertical lines
    horizontal_lines = []
    vertical_lines = []
    for x1, y1, x2, y2 in rail_lines:
        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
        if angle < 15 or angle > 165:  # Horizontal
            horizontal_lines.append((x1, y1, x2, y2))
        elif 75 < angle < 105:  # Vertical
            vertical_lines.append((x1, y1, x2, y2))

    # Sort lines to get the top, bottom, left, and right inside edges
    horizontal_lines.sort(key=lambda line: (line[1] + line[3]) / 2)  # Sort by y-coordinate
    vertical_lines.sort(key=lambda line: (line[0] + line[2]) / 2)    # Sort by x-coordinate

    # Refine to find edges closest to the felt
    top_edge = horizontal_lines[0] if horizontal_lines else None
    bottom_edge = horizontal_lines[-1] if horizontal_lines else None
    left_edge = vertical_lines[0] if vertical_lines else None
    right_edge = vertical_lines[-1] if vertical_lines else None

    return top_edge, bottom_edge, left_edge, right_edge

def draw_inside_border(image, edges):
    """
    Draw a complete border around the inside edges of the pool table closest to the felt.
    
    Args:
        image (numpy array): Input image as a numpy array.
        edges (list): Four edges of the table (top, bottom, left, right).
    """
    top_edge, bottom_edge, left_edge, right_edge = edges

    if top_edge and bottom_edge and left_edge and right_edge:
        # Get the corner points of the border
        top_left = (left_edge[0], top_edge[1])
        top_right = (right_edge[0], top_edge[1])
        bottom_left = (left_edge[0], bottom_edge[1])
        bottom_right = (right_edge[0], bottom_edge[1])

        # Draw the border
        cv2.line(image, top_left, top_right, (0, 255, 0), 2)  # Top edge
        cv2.line(image, top_right, bottom_right, (0, 255, 0), 2)  # Right edge
        cv2.line(image, bottom_right, bottom_left, (0, 255, 0), 2)  # Bottom edge
        cv2.line(image, bottom_left, top_left, (0, 255, 0), 2)  # Left edge

        # Display coordinates at each corner
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (255, 0, 0)  # Blue text
        thickness = 1

        cv2.putText(image, f"{top_left}", top_left, font, font_scale, color, thickness)
        cv2.putText(image, f"{top_right}", top_right, font, font_scale, color, thickness)
        cv2.putText(image, f"{bottom_left}", bottom_left, font, font_scale, color, thickness)
        cv2.putText(image, f"{bottom_right}", bottom_right, font, font_scale, color, thickness)

        edges_coordinates = [
            [top_left, top_right],       # Top edge
            [bottom_left, bottom_right], # Bottom edge
            [top_left, bottom_left],     # Left edge
            [top_right, bottom_right]    # Right edge
        ]

        return edges_coordinates

def perfect_edges(top_edge, bottom_edge, left_edge, right_edge):
   # x1, y1, x2, y2 
    # Unpack initial coordinates
    print(top_edge)
    top_left_x1, top_left_y1, top_right_x1, top_right_y1 = top_edge
    bottom_left_x1, bottom_left_y1, bottom_right_x1, bottom_right_y1 = bottom_edge
    top_left_x2, top_left_y2, bottom_left_x2, bottom_left_y2 = left_edge
    top_right_x2, top_right_y2, bottom_right_x2, bottom_right_y2 = right_edge
    
    # Ensure top and bottom edges are perfectly horizontal
    top_edge = (top_left_x1, top_left_y1, top_right_x1, top_left_y1)
    bottom_edge = (bottom_left_x1, bottom_left_y1, bottom_right_x1, bottom_left_y1)
    
    # Ensure left and right edges are perfectly vertical
    left_edge = (top_left_x2, top_left_y1, top_left_x2, bottom_left_y1)
    right_edge = (top_right_x2, top_right_y1, top_right_x2, bottom_right_y1)
    
    return (top_edge, bottom_edge, left_edge, right_edge)

def format_coordinates(input_coords):
    top, bottom, left, right = input_coords
    
    top_cords = [
        (top[0], top[1]),     # First point of top edge
        (top[2], top[3])      # Second point of top edge
    ]
    
    bottom_cords = [
        (bottom[0], bottom[1]),   # First point of bottom edge
        (bottom[2], bottom[3])    # Second point of bottom edge
    ]
    
    left_cords = [
        (left[0], left[1]),   # First point of left edge
        (left[2], left[3])    # Second point of left edge
    ]
    
    right_cords = [
        (right[0], right[1]),   # First point of right edge
        (right[2], right[3])    # Second point of right edge
    ]
    
    return top_cords, bottom_cords, left_cords, right_cords

def crop_image(image, top_cords, bottom_cords, left_cords, right_cords):
    top_y = min(top_cords[1], top_cords[3])
    bottom_y = max(bottom_cords[1], bottom_cords[3])
    left_x = min(left_cords[0], left_cords[2])
    right_x = max(right_cords[0], right_cords[2])

    cropped_image = image[top_y:bottom_y, left_x:right_x]
    return cropped_image

def getBorder(image):
    """
    Main function to process the image and draw the pool table's inside border.
    
    Args:
        image_path (str): Path to the input image.
    """
 
    
    # Detect inside rail edges
    rail_lines = enhanced_rail_detection(image)
    print("HERE")
    # Get the main inside table edges
    edges = get_inside_table_edges(rail_lines)
    edges_formated = draw_inside_border(image, edges)

    # cv2.imshow('Inside Rail Edges', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
 
    # edges = perfect_edges(top_edge=edges[0], bottom_edge=edges[1], left_edge=edges[2], right_edge=edges[3])
    # top_cords, bottom_cords, left_cords, right_cords = format_coordinates(edges)

    # image = crop_image(image, top_cords, bottom_cords, left_cords, right_cords)
    return image, edges_formated


    

# main("/Users/jacobleader/Desktop/Code/CueTips/data/pool_table_overhead.png")

