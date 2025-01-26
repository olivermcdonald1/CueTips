import cv2
import numpy as np
from PoolBall import PoolBall

def preprocess(img):
  
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return blurred

def plotCircles(img, circles):
    pool_balls = []
    avg_radius = 0  # Default

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        radius_list = [circle[2] for circle in circles]
        min_radius = min(radius_list)
        avg_radius = int(sum(radius_list) / len(radius_list))
        
        for (x, y, r) in circles:
            if r > min_radius * 2:  # Ignore large circles that are likely not balls
                continue
            
            # Calculate the average color within the circle
            mask = np.zeros(img.shape[:2], dtype="uint8")
            cv2.circle(mask, (x, y), r, 255, -1)  # Mask the circle
            mean_color = cv2.mean(img, mask=mask)  # Extract mean color from masked region
            color = tuple(map(int, mean_color[:3]))  # Convert BGR to integer RGB

            # Create a PoolBall with the detected properties
            pool_ball = PoolBall(x, y, color=color, suit="solid")
            pool_balls.append(pool_ball)
            
            print(f"Circle: x-cord: {x}, y-cord: {y}, radius: {r}, color: {color}")
            
            # Draw the circle and color on the image
            cv2.circle(img, center=(x, y), radius=r, color=color, thickness=-1)  # Fill with the detected color

        buildBorder(circles, min_radius)
    
    return img, pool_balls, avg_radius

def displayBalls(pool_balls, img, radius):
    """
    Place the detected pool balls onto the pool table background.
    """
    for pool_ball in pool_balls:
        x, y = pool_ball.x_cord, pool_ball.y_cord
        
        # Draw the cartoon ball on the pool table image
        cv2.circle(img, (x, y), radius, pool_ball.color, -1)
        
        # Add the suit number (solid/striped) or similar identifier to the ball
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(pool_ball.suit), (x - 5, y + 5), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    
    return img

def showImgs(img, cartoon_img):
    cv2.imshow("OG img", img)
    cv2.imshow("cartoon", cartoon_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def buildBorder(circles, min_radius):
    pockets = []
    for (x, y, r) in circles:
            if r > 61: 
                pocket = PoolBall(x,y,color=(0,0,0),suit="none",radius = r)
                pockets.append(pocket)
    for pocket in pockets:
        print(pocket)

def createPocketsFromEdges(edges):
    """
    Create the pocket positions from the given edges (top, bottom, left, right).
    """
    top_cords, bottom_cords, left_cords, right_cords = edges
    # Extract corner points
    top_left = top_cords[0]
    top_right = top_cords[1]
    bottom_left = bottom_cords[0]
    bottom_right = bottom_cords[1]
    
    # Middle pocket positions (calculate center of top and bottom edges)
    left_middle = ((left_cords[0][0] + left_cords[1][0]) // 2, (left_cords[0][1] + left_cords[1][1]) // 2)
    right_middle = ((right_cords[0][0] + right_cords[1][0]) // 2, (right_cords[0][1] + right_cords[1][1]) // 2)
    
    # Pocket positions: corners + middle of left and right edges
    pocket_positions = [top_left, top_right, bottom_left, bottom_right, left_middle, right_middle]
    
    return pocket_positions

def addPoolTable(img, pocket_positions, edges, pool_ball_size):
    """
    Draw the modern pool table with pockets, using the edges passed.
    """
    top_left = tuple(edges[0][0])  # top-left corner
    bottom_right = tuple(edges[3][1])  # bottom-right corner
    table_color = (0, 128, 0)  # Green
    cv2.rectangle(img, top_left, bottom_right, table_color, -1)
    
    pocket_radius = int(pool_ball_size * 2.5)
    for pos in pocket_positions:
        cv2.circle(img, pos, pocket_radius, (0, 0, 0), -1)  # Black Color

    return img

def cartoonify(img, edges):
    '''
    input: numpy.ndarray
    output: numpy.ndarray, [PoolBalls]
    '''
    
    blurred = preprocess(img)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=60, param1=50, param2=25, minRadius=20, maxRadius=30)

        
    top_edge = edges[0]
    left_edge = edges[2]
    WIDTH = top_edge[1][0] - top_edge[0][0]
    HEIGHT = left_edge[1][1] - left_edge[0][1]
    pocket_positions = createPocketsFromEdges(edges) 
    
    img, pool_balls, avg_radius = plotCircles(img, circles)

    blank_canvas = np.zeros((HEIGHT, WIDTH, 3), dtype="uint8")
    cartoon_table = addPoolTable(blank_canvas, pocket_positions, edges, avg_radius)
    cartoon_balls = displayBalls(pool_balls, cartoon_table, radius=avg_radius)
    # showImgs(img, cartoon_img)  # Uncomment
    
    return cartoon_balls, pool_balls, avg_radius, pocket_positions
    
# Testing
if __name__ == '__main__':
    table_coordinates = np.float32([[415, 239], [172, 1121],
                       [1575, 1158], [1380, 243]])
    
    cartoon_img, pool_balls, avg_radius = cartoonify(table_coordinates)
    # If you need to save the image after cartoonification:
    # cv2.imwrite("cartoonified_pool_table.png", cartoon_img)
