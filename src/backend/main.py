from Cartoonify import *
from ImageTo2d import *
import cv2

if __name__ == '__main__':
    birds_eye_image,corners = getOutlineAndTransform("data/pool_table_overhead.png", padding=40)
    
    cartoon_img, pool_balls = cartoonify(corners,birds_eye_image)

    cv2.imshow("birds eye", birds_eye_image)
    cv2.imshow("cartoon", cartoon_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()