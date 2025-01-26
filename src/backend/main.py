from Cartoonify import *
from ImageTo2d import *
from Border import *
from physics.simulatePaths import main  # We'll update simulatePaths soon
import cv2

def getCueTips(img):
    birds_eye_image, corners = getOutlineAndTransform("data/pool_table_overhead.png", padding=40)
    cropped_img, edges = getBorder(birds_eye_image)
    cartoon_img, pool_balls, avg_radius = cartoonify(corners, cropped_img)

    paths = main(pool_balls, cue_ball=None, wall_cords=edges, ball_radius=avg_radius)
    
    return cartoon_img, paths
    
    
if __name__ == '__main__':
    
    birds_eye_image, corners = getOutlineAndTransform("data/pool_table_overhead.png", padding=40)

   
    cartoon_img, pool_balls, avg_radius = cartoonify(corners, birds_eye_image)
    
   
    old_w, old_h = 1438, 2538
    new_w, new_h = 400, 800
    scale_x = new_w / old_w
    scale_y = new_h / old_h
    
    for pool_ball in pool_balls:
        pool_ball.x_cord = int(pool_ball.x_cord * scale_x)
        pool_ball.y_cord = int(pool_ball.y_cord * scale_y)


    main(pool_balls, cue_ball=None, wall_cords=None, ball_radius=avg_radius)


    cv2.imshow("birds eye", birds_eye_image)
   
    cv2.waitKey(0)
    cv2.destroyAllWindows()