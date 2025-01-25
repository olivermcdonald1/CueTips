import cv2
import numpy as np

def order_corners(corners):
    rect = np.zeros((4, 2), dtype="float32")
    s = corners.sum(axis=1)
    diff = np.diff(corners, axis=1)

    rect[0] = corners[np.argmin(s)]     
    rect[2] = corners[np.argmax(s)]    
    rect[1] = corners[np.argmin(diff)]  
    rect[3] = corners[np.argmax(diff)]  

    return rect

def add_padding(corners, padding, image_width, image_height):

    corners[0] -= padding 
    corners[1] += [padding, -padding]  
    corners[2] += padding 
    corners[3] += [-padding, padding] 


    corners[:, 0] = np.clip(corners[:, 0], 0, image_width - 1)  
    corners[:, 1] = np.clip(corners[:, 1], 0, image_height - 1) 

    return corners

def getOutlineAndTransform(image_path, padding=10):
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load image. Check the file path.")
        return None, None

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = (30, 40, 40)
    upper_green = (85, 255, 255)

    mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No green region found! Try adjusting the HSV range or check lighting.")
        return None, None

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    table_contour = contours[0]

    peri = cv2.arcLength(table_contour, True)
    approx = cv2.approxPolyDP(table_contour, 0.02 * peri, True)

    if len(approx) < 4:
        print("Could not approximate a 4-corner table. Found:", len(approx))
        return None, None

    corners = approx.reshape(-1, 2).astype("float32")
    ordered_corners = order_corners(corners)

    height, width = image.shape[:2]
    padded_corners = add_padding(ordered_corners, padding, width, height)

    output_width = int(np.linalg.norm(padded_corners[1] - padded_corners[0]))  # Top width
    output_height = int(np.linalg.norm(padded_corners[3] - padded_corners[0]))  # Left height

    dst_points = np.array([
        [0, 0],
        [output_width - 1, 0],
        [output_width - 1, output_height - 1],
        [0, output_height - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(padded_corners, dst_points)
    warped = cv2.warpPerspective(image, M, (output_width, output_height))

    return warped, padded_corners


if __name__ == "__main__":
    getOutlineAndTransform("/Users/olivermcdonald/CueTips/data/pool_table_overhead.png", padding=40)