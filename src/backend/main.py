from Cartoonify import *
from ImageTo2d import *
from Border import *
from physics.simulatePaths import main  # We'll update simulatePaths soon
import cv2

def getCueTips(img):
    birds_eye_image, corners = getOutlineAndTransform(img, padding=40)
    print("getting cue tips")
    cropped_img, edges = getBorder(birds_eye_image)
    print("Got edges")
    # print("got border")
    # cartoon_img, pool_balls, avg_radius = cartoonify(corners, birds_eye_image)

    paths = main(pool_balls, cue_ball=None, wall_cords=edges, ball_radius=avg_radius, show_simulation=False)
    # Return paths in the future
    return birds_eye_image
    
 
if __name__ == '__main__':
    img = cv2.imread("data/pool_table_overhead.png")
    birds_eye_image, corners = getOutlineAndTransform(img, padding=40)
    cropped_img, edges = getBorder(birds_eye_image)
    
    cartoon_img, pool_balls, avg_radius = cartoonify(corners, birds_eye_image)

    # cv2.imshow("cartoon", cartoon_img)
    # cv2.imshow("birds eye", birds_eye_image)
   
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # exit()
    tempfile_svg_name = main(pool_balls, cue_ball=None, wall_cords=edges, ball_radius=avg_radius, cue_angle=280, show_simulation=False)
    print(tempfile_svg_name)
    
    with open(tempfile_svg_name, 'r') as file:
        svg_content = file.read()

    print("SVG Content:")
    print(svg_content)
