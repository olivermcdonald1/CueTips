from Cartoonify import *
from ImageTo2d import *
from Border import *
from physics.simulatePaths import main  # We'll update simulatePaths soon
import cv2
from PIL import Image, ImageDraw
import cairosvg
import xml.etree.ElementTree as ET

def svg_to_opencv_lines(svg_content):
    # Parse the SVG file using ElementTree
    root = ET.fromstring(svg_content)
    lines = []
    
    # Extract line coordinates from the SVG
    for line in root.findall(".//{http://www.w3.org/2000/svg}line"):
        x1 = float(line.get('x1'))
        y1 = float(line.get('y1'))
        x2 = float(line.get('x2'))
        y2 = float(line.get('y2'))
        lines.append((x1, y1, x2, y2))
    
    return lines

def overlay_svg_lines_on_image(image_path, svg_content):
    # Load the image using OpenCV
    
    # Convert SVG lines into OpenCV compatible format
    lines = svg_to_opencv_lines(svg_content)
    
    # Draw the lines on the image
    for (x1, y1, x2, y2) in lines:
        cv2.line(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 255), 2)  # white lines
    
    return image

def getCueTips(img, run_sim):

    birds_eye_image, corners = getOutlineAndTransform(img, padding=40)
    print("getting cue tips")
    cropped_img, edges = getBorder(birds_eye_image)
    print("Got edges")
    
    cartoon_img, pool_balls, avg_radius, pockets = cartoonify(birds_eye_image, edges)

    tempfile_svg_name = ''
    cue_ball_coords = (0,0) 
    if run_sim:
        tempfile_svg_name, cue_ball_coords = main(pool_balls, wall_cords=edges, ball_radius=avg_radius, cue_angle=45, show_simulation=True)   
         
    with open(tempfile_svg_name, 'r') as file:
        svg_content = file.read()
    
    print(svg)
    path_img = overlay_svg_lines_on_image(cartoon_img, svg_content) 
    cv2.imshow("path", path_img)
    cv2.waitKey(0)
    
    return cartoon_img, tempfile_svg_name, cue_ball_coords, (pool_balls, edges, avg_radius)


if __name__ == '__main__':
    img = cv2.imread("data/pool_table_overhead.png")
    getCueTips(img, run_sim=True)
    
  
    # birds_eye_image, corners = getOutlineAndTransform(img, padding=40)
    # cropped_img, edges = getBorder(birds_eye_image)

    # cartoon_img, pool_balls, avg_radius = cartoonify(corners, birds_eye_image)

    # cv2.imshow("cartoon", cartoon_img)
    # cv2.imshow("birds eye", birds_eye_image)
   
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # exit()
    # tempfile_svg_name = main(pool_balls, cue_ball=None, wall_cords=edges, ball_radius=avg_radius, cue_angle=280, show_simulation=False)
    # print(tempfile_svg_name)
    
   

