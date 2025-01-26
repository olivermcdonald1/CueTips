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

def get_prominent_color(image):
    """
    Finds the prominent color in the center of the image.
    """
    height, width = image.shape[:2]
    center_region = image[height // 3 : 2 * height // 3, width // 3 : 2 * width // 3]
    

    avg_bgr = np.mean(center_region, axis=(0, 1))
    
    avg_hsv = cv2.cvtColor(np.uint8([[avg_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
    
    return avg_hsv

def getOutlineAndTransform(image_path, padding=50):
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not load image. Check the file path.")
        return None, None

    avg_hsv = get_prominent_color(image)
    lower_hsv = np.array([max(0, avg_hsv[0] - 10), max(0, avg_hsv[1] - 50), max(0, avg_hsv[2] - 50)])
    upper_hsv = np.array([min(179, avg_hsv[0] + 10), min(255, avg_hsv[1] + 50), min(255, avg_hsv[2] + 50)])

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_hsv, upper_hsv)


    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No table detected. Try adjusting lighting or HSV thresholds.")
        return None, None

 
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    table_contour = contours[0]

    peri = cv2.arcLength(table_contour, True)
    approx = cv2.approxPolyDP(table_contour, 0.02 * peri, True)

    if len(approx) < 4:
        print("Could not approximate a 4-corner table. Found:", len(approx))
        return None, None

    # Order corners and add padding
    corners = approx.reshape(-1, 2).astype("float32")
    ordered_corners = order_corners(corners)

    height, width = image.shape[:2]
    padded_corners = add_padding(ordered_corners, padding, width, height)


    output_width = int(np.linalg.norm(padded_corners[1] - padded_corners[0]))
    output_height = int(np.linalg.norm(padded_corners[3] - padded_corners[0]))

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
    warped, corners = getOutlineAndTransform("/Users/olivermcdonald/CueTips/data/pool_table_overhead.png", padding=40)
    if warped is not None:
        cv2.imshow("Warped Pool Table", warped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()