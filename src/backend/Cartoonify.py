import cv2
import numpy as np
from PoolBall import PoolBall

def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    return blurred

def plotCircles(img, circles):
    pool_balls = []
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")  # Round and convert to integer
        radius_list = [circle[2] for circle in circles]
        min_radius = min(radius_list)
        avg_radius = int(sum(radius_list)/len(radius_list))
        for (x, y, r) in circles:
            if r > min_radius * 1.3: # Pockets
                continue
            
            pool_ball = PoolBall(x, y, color=(0, 255, 0), suit="solid")
            pool_balls.append(pool_ball)
            
            print(f"Circle: x-cord: {x}, y-cord: {y}, radius: {r}")
            
            # Draw the circle on the image
            cv2.circle(img, center=(x, y), radius=r, color=(0, 255, 0), thickness=4)  # Green circle
    
        # cv2.imshow(img)
        # cv2.waitKey(0)
        print(img)
        print(pool_balls)
        return img, pool_balls, avg_radius

def displayBalls(pool_balls, table_coordinates, img_shape, radius):
    img = np.ones((img_shape[0], img_shape[1], 3), dtype=np.uint8) * 255  # Blank white

    top_right, top_left, bottom_left, bottom_right = table_coordinates
    
    for pool_ball in pool_balls:
        x, y = pool_ball.x_cord, pool_ball.y_cord
        
        cv2.circle(img, (x, y), radius, pool_ball.color, -1)     
                
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(pool_ball.suit), (x - 5, y + 5), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    
    return img

def showImgs(img, cartoon_img):
    cv2.imshow("OG img", img)
    cv2.imshow("cartoon", cartoon_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def cartoonify(table_coordinates, img=cv2.imread('data/pool_table_overhead.png')):
    '''
    input: numpy.ndarray
    output: numpy.ndarray, [PoolBalls]
    '''
    
    blurred = preprocess(img)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=1, param1=50, param2=30, minRadius=3, maxRadius=50)

    img, pool_balls, avg_radius = plotCircles(img, circles)
    
    cartoon_img = displayBalls(pool_balls, table_coordinates, img_shape=img.shape, radius=avg_radius)
    
    # showImgs() # Comment out

    return cartoon_img, pool_balls
    
# Testing
if __name__ == '__main__':
    table_coordinates = np.float32([[415, 239], [172, 1121],
                       [1575, 1158], [1380, 243]])
    cartoonify(table_coordinates)
    