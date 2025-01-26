from Cartoonify import *
from ImageTo2d import *
from Border import *
from physics.simulatePaths import simulatePaths
import cv2

if __name__ == '__main__':
    
    birds_eye_image,corners = getOutlineAndTransform("/Users/olivermcdonald/CueTips/data/pool_table_overhead.png", padding=40)
   
    cartoon_img, pool_balls, avg_radius = cartoonify(corners,birds_eye_image)
    
    paths = simulatePaths(pool_balls, cue_ball=None, wall_cords, ball_radius=avg_radius)

    cv2.imshow("birds eye", birds_eye_image)
    #cv2.imshow("cartoon", cartoon_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()