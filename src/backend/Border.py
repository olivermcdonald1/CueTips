import cv2
import numpy as np

def find_pool_table_outline(image_path, debug=False):
    """
    Detects the rectangular boundary of a pool table in the image and
    returns an image with the detected outline drawn.
    
    :param image_path: Path to the pool table image.
    :param debug: Whether to show intermediate steps for debugging.
    :return: (outline_image, corners) where
             outline_image is the original image with the boundary drawn,
             corners is a list of 4 corner points [top-left, top-right, bottom-right, bottom-left].
    """
    
    # 1. Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read the image at {image_path}")

    original = img.copy()
    height, width = img.shape[:2]

    # 2. Convert to grayscale and blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 3. Edge detection
    edges = cv2.Canny(gray, threshold1=80, threshold2=40, apertureSize=3)

    # 4. Hough line transform to detect lines
    #    Adjust parameters as needed (e.g., the threshold, minLineLength, maxLineGap)
    lines = cv2.HoughLinesP(
    edges,
    rho=1,
    theta=np.pi/180,
    threshold=80,            # Lower threshold to detect more lines
    minLineLength=100,        # Possibly shorter lines
    maxLineGap=20
)

    if debug:
        debug_lines = original.copy()
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(debug_lines, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imshow("Detected Lines (Debug)", debug_lines)
        cv2.waitKey(0)

    # Make sure lines were found
    if lines is None or len(lines) == 0:
        print("No table lines detected!")
        return original, []

    # 5. Separate lines into near-vertical and near-horizontal
    #    This helps cluster them into the 4 edges of the table
    vertical_lines = []
    horizontal_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        dx = x2 - x1
        dy = y2 - y1
        angle = abs(np.arctan2(dy, dx) * 180.0 / np.pi)

        # Heuristic: if angle < 30 or > 150, treat as horizontal
        #            if angle is near 90, treat as vertical
        if angle < 30 or angle > 150:
            horizontal_lines.append(line[0])
        else:
            vertical_lines.append(line[0])

    # Optional: Further cluster or average lines that are close together
    #           so we end up with one representative line per side.

    def average_line(lines_array):
        """Averaging function to 'merge' lines that are roughly in the same location."""
        if len(lines_array) == 0:
            return None
        x1_vals, y1_vals, x2_vals, y2_vals = [], [], [], []
        for (x1, y1, x2, y2) in lines_array:
            x1_vals.append(x1)
            y1_vals.append(y1)
            x2_vals.append(x2)
            y2_vals.append(y2)
        return (
            int(np.mean(x1_vals)),
            int(np.mean(y1_vals)),
            int(np.mean(x2_vals)),
            int(np.mean(y2_vals))
        )

    horiz_line_1 = average_line(horizontal_lines)
    vert_line_1 = average_line(vertical_lines)

    # If we only do one average per set, we might lose edges if multiple lines exist.
    # In practice, you might detect 2 main horizontal lines & 2 main vertical lines:
    # For simplicity, let's assume we somehow extracted the top, bottom, left, and right lines properly.

    # A more robust approach:
    #  (a) group horizontal lines by y-intercept proximity,
    #  (b) group vertical lines by x-intercept proximity,
    #  (c) choose the extreme (topmost, bottommost, leftmost, rightmost) lines.

    # For demonstration, let's pick the two extremes in each direction:
    def find_extreme_lines(lines_array, orientation='horizontal'):
        """
        Finds the two extreme lines from a list of lines (either top-most & bottom-most
        if horizontal, or left-most & right-most if vertical).
        """
        if len(lines_array) < 2:
            return None, None
        # For horizontal lines, compare their y-values.
        # For vertical lines, compare their x-values.
        if orientation == 'horizontal':
            # compute average y for each line
            lines_sorted = sorted(lines_array, key=lambda l: (l[1] + l[3]) / 2.0)
        else:
            # vertical
            lines_sorted = sorted(lines_array, key=lambda l: (l[0] + l[2]) / 2.0)

        return average_line([lines_sorted[0]]), average_line([lines_sorted[-1]])

    top_line, bottom_line = find_extreme_lines(horizontal_lines, orientation='horizontal')
    left_line, right_line = find_extreme_lines(vertical_lines, orientation='vertical')

    # Quick check in case detection failed
    if not all([top_line, bottom_line, left_line, right_line]):
        print("Could not find all table edges reliably.")
        return original, []

    def line_to_abc(line):
        """Convert line segment (x1, y1, x2, y2) to A,B,C of line equation Ax + By + C=0."""
        x1, y1, x2, y2 = line
        A = y2 - y1
        B = x1 - x2
        C = x2*y1 - x1*y2
        return A, B, C

    def intersect_lines(line1, line2):
        """Find intersection of two lines in ABC form."""
        A1, B1, C1 = line_to_abc(line1)
        A2, B2, C2 = line_to_abc(line2)

        determinant = A1 * B2 - A2 * B1
        if abs(determinant) < 1e-10:
            return None  

        x = (B2 * (-C1) - B1 * (-C2)) / determinant
        y = (A1 * (-C2) - A2 * (-C1)) / determinant
        return (int(x), int(y))

    # corners = [
    #   intersect(top_line, left_line),
    #   intersect(top_line, right_line),
    #   intersect(bottom_line, left_line),
    #   intersect(bottom_line, right_line)
    # ]
    top_left     = intersect_lines(top_line, left_line)
    top_right    = intersect_lines(top_line, right_line)
    bottom_left  = intersect_lines(bottom_line, left_line)
    bottom_right = intersect_lines(bottom_line, right_line)

    corners = [top_left, top_right, bottom_right, bottom_left]

    # 7. Draw the detected rectangle on the image
    outline_image = original.copy()
    # If desired, we can also refine the corners by bounding them to image extents
    # or adjusting them if there's any confidence measure.
    for i in range(len(corners)):
        pt1 = corners[i]
        pt2 = corners[(i + 1) % len(corners)]
        if pt1 is None or pt2 is None:
            continue
        cv2.line(outline_image, pt1, pt2, (0, 0, 255), 3)

    # For debugging, mark corners as well
    for corner in corners:
        if corner is not None:
            cv2.circle(outline_image, corner, 8, (0, 255, 0), -1)

    if debug:
        cv2.imshow("Detected Table Outline", outline_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return outline_image, corners

if __name__ == "__main__":

    image_path = "/Users/olivermcdonald/CueTips/data/pool_table_overhead.png"  # replace with your image path
    outline_image, corners = find_pool_table_outline(image_path, debug=True)
    
    print("Detected corners (in order):", corners)
    # corners should be [top-left, top-right, bottom-right, bottom-left]

    # Save the output if desired
    cv2.imwrite("pool_table_outline_detected.jpg", outline_image)