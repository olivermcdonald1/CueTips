import sys
import math
import random
import pygame
import pymunk
import svgwrite
import io
import tempfile

space = pymunk.Space()
space.gravity = (0, 0)

collisions = []
last_positions = {}

def calculate_deceleration(velocity, friction_coefficient, delta_time):
    """
    Simulates the deceleration of a pool ball due to table friction.

    Parameters:
        velocity (tuple): Current velocity of the ball as (vx, vy).
        friction_coefficient (float): Coefficient of kinetic friction (depends on table material).
        delta_time (float): Time step in seconds.

    Returns:
        tuple: Updated velocity (vx, vy) after deceleration.
    """
    # Compute the speed (magnitude of velocity)
    speed = math.sqrt(velocity[0]**2 + velocity[1]**2)

    if speed == 0:
        return (0, 0)  # Ball is already at rest

    # Deceleration due to friction: F = friction_coefficient * g (g = 9.8 m/s^2)
    deceleration = friction_coefficient * 9.8

    # Reduce speed based on deceleration and time step
    new_speed = max(0, speed - deceleration * delta_time)

    # Scale velocity components to match the new speed
    scale = new_speed / speed if speed > 0 else 0
    new_velocity = (velocity[0] * scale, velocity[1] * scale)

    return new_velocity

def on_collision_ball_ball(arbiter, space, data):
    shape_a, shape_b = arbiter.shapes

    for shape in (shape_a, shape_b):
        if shape.collision_type == 1: 
            current_pos = shape.body.position
            
            if shape in data["last_positions"]:
                start_pos = data["last_positions"][shape]
            else:
                start_pos = (current_pos.x, current_pos.y)

            end_pos = (current_pos.x, current_pos.y)
            
            if start_pos != end_pos:
                ball_color = shape.color if hasattr(shape, 'color') else (255, 255, 255)
                data["collisions"].append((start_pos, end_pos, ball_color))
            
            data["last_positions"][shape] = end_pos

    return True

def on_collision_ball_wall(arbiter, space, data):
    shape_a, shape_b = arbiter.shapes

    if shape_a.collision_type == 1:
        ball_shape = shape_a
    else:
        ball_shape = shape_b

    current_pos = ball_shape.body.position
    
    if ball_shape in data["last_positions"]:
        start_pos = data["last_positions"][ball_shape]
    else:
        start_pos = (current_pos.x, current_pos.y)

    end_pos = (current_pos.x, current_pos.y)
    
    if start_pos != end_pos:
        ball_color = ball_shape.color if hasattr(ball_shape, 'color') else (255, 255, 255)
        data["collisions"].append((start_pos, end_pos, ball_color))
    
    data["last_positions"][ball_shape] = end_pos

    return True

def on_collision_ball_pocket(arbiter, space, data):
    """Handles ball-pocket collisions. Removes the ball from the simulation."""
    ball_shape, pocket_shape = arbiter.shapes

    if ball_shape.collision_type == 1:  # Confirm it's a ball
        space.remove(ball_shape, ball_shape.body)

    return False  # End collision processing

class SimulatedBall:
    def __init__(self, x, y, radius, color, velocity=(0, 0)):
        self.radius = radius
        self.color = color

        self.body = pymunk.Body(mass=1, moment=pymunk.moment_for_circle(1, 0, radius))
        self.body.position = (x, y)
        self.body.velocity = velocity

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.06
        self.shape.elasticity = 0.9
        self.shape.collision_type = 1
        self.shape.color = color

        space.add(self.body, self.shape)

        last_positions[self.shape] = (x, y)

    def draw(self, screen):
        pos = self.body.position
        pygame.draw.circle(screen, self.color, (int(pos.x), int(pos.y)), self.radius)


def save_paths_as_svg(collisions, WIDTH, HEIGHT):
    # Create a temporary file to store the SVG content
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.svg')

    # Create the SVG drawing and write directly to the temporary file
    dwg = svgwrite.Drawing(temp_file.name, profile='tiny', size=(str(WIDTH), str(HEIGHT)))
    
    # Add the background rectangle (pool table green)
    dwg.add(dwg.rect(insert=(0, 0), size=(str(WIDTH), str(HEIGHT)), fill='rgb(38, 141, 44)'))
    
    # Add the collision lines
    for start, end, color in collisions:
        svg_color = f'rgb({color[0]},{color[1]},{color[2]})'
        dwg.add(dwg.line(
            start=(start[0], start[1]),
            end=(end[0], end[1]),
            stroke=svg_color,
            stroke_width=2
        ))
    
    # Save the SVG content directly to the temporary file
    dwg.save()

    # Return the path to the temporary file
    return temp_file.name

    
def create_borders(edges):
    top, bottom, left, right = edges
    walls = [
        pymunk.Segment(space.static_body, (top[0][0], top[0][1]), (top[1][0], top[1][1]), 5),
        pymunk.Segment(space.static_body, (bottom[0][0], bottom[0][1]), (bottom[1][0], bottom[1][1]), 5),
        pymunk.Segment(space.static_body, (left[0][0], left[0][1]), (left[1][0], left[1][1]), 5),
        pymunk.Segment(space.static_body, (right[0][0], right[0][1]), (right[1][0], right[1][1]), 5)
    ]
    for wall in walls:
        wall.friction = 0.14
        wall.elasticity = 0.9
        wall.collision_type = 2
        space.add(wall)

def create_pockets(WIDTH, HEIGHT):
    """Create 6 pockets for the pool table with visual outlines."""
    pocket_radius = 20
    pocket_positions = [
        (10, 10),  
        (10, (WIDTH // 2)+200), 
        (WIDTH - 10, 10), 
        (10, HEIGHT - 10), 
        ((WIDTH // 2)+192, HEIGHT//2),  
        (WIDTH - 10, HEIGHT - 10)  
    ]

    pockets = []
    for pos in pocket_positions:
        pocket_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        pocket_shape = pymunk.Circle(pocket_body, pocket_radius)
        pocket_body.position = pos
        pocket_shape.collision_type = 3  # Pocket collision type
        space.add(pocket_body, pocket_shape)
        pockets.append((pos, pocket_radius))

    return pockets

def draw_pockets(screen, pockets):
    
    for pos, radius in pockets:
        pygame.draw.circle(screen, (255, 255, 255), (int(pos[0]), int(pos[1])), radius, 2)  # White outline

def get_cue_ball(pool_balls, max_color_diff=100):
    def color_distance(color1, color2):
        # Euclidean distance between two colors in RGB space
        return math.sqrt((color1[0] - color2[0]) ** 2 + (color1[1] - color2[1]) ** 2 + (color1[2] - color2[2]) ** 2)

    remaining_balls = []
    closest_ball = None
    closest_color_diff = float('inf') 

    for ball in pool_balls:        
        color_diff = color_distance(ball.color, (255, 255, 255))

        # If the ball is closer to white and within the color difference threshold, keep it
        if color_diff < closest_color_diff and color_diff <= max_color_diff:
            closest_color_diff = color_diff
            if closest_ball:
                remaining_balls.append(closest_ball)
            closest_ball = ball
        else:
            remaining_balls.append(ball)

    return closest_ball, remaining_balls

def run_game(balls, screen, clock, pockets, show_simulation, WIDTH, HEIGHT):
    running = True
    friction_coefficient = 0.7  #

    cue_ball = next((b for b in balls if b.color == (255, 255, 255)), None)
    if not cue_ball:
        raise ValueError("Cue ball is required for the simulation")

    while running:
        still_moving = any(abs(ball.body.velocity[0]) > 0 or abs(ball.body.velocity[1]) > 0 for ball in balls)
        if not still_moving:
            print("All balls have stopped")
            break

        # Apply velocity to the cue ball in the direction of the provided angle when stationary
        # if cue_ball.body.velocity.length == 0 and cue_angle is not None:
        #     speed = 200  # Set the desired speed of the cue ball
        #     cue_ball.body.velocity = (
        #         speed * math.cos(cue_angle),
        #         speed * math.sin(cue_angle)
        #     )

        for ball in balls:
            velocity = ball.body.velocity
            ball.body.velocity = calculate_deceleration((velocity.x, velocity.y), friction_coefficient, 1/50.0)

        if show_simulation:
            space.step(1/50.0)
        else:
            space.step(1/50.0)

        screen.fill((38, 141, 44))

        draw_pockets(screen, pockets)  #

        for b in balls:
            if b.body in space.bodies:
                b.draw(screen)

        for line_seg in collisions:
            start, end, color = line_seg
            pygame.draw.line(screen, color,
                             (int(start[0]), int(start[1])),
                             (int(end[0]), int(end[1])),
                             2)

        pygame.display.flip()
        if show_simulation:
            clock.tick(50)
        else:
           clock.tick(100_000) 

    # Save the collisions as an SVG when the simulation ends
    tempfile_svg_name = save_paths_as_svg(collisions, WIDTH, HEIGHT)
    print("SAVED SVG")
    
    pygame.quit()
        
    return tempfile_svg_name 


# Add this modification to save the paths to an SVG file whenever the simulation ends.
# The saved SVG can then be embedded into a website using standard HTML <img> tags or <object> tags.



def main(pool_balls, wall_cords=None, ball_radius=15, cue_angle=0, show_simulation=True):
    global collisions, last_positions
    collisions = []
    last_positions = {}

    pygame.init()
    
    top_edge = wall_cords[0]
    left_edge = wall_cords[2]
    WIDTH = top_edge[1][0] - top_edge[0][0]
    HEIGHT = left_edge[1][1] - left_edge[0][1]
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    create_borders(wall_cords)

    handler_bb = space.add_collision_handler(1, 1)
    handler_bb.begin = on_collision_ball_ball
    handler_bb.data["collisions"] = collisions
    handler_bb.data["last_positions"] = last_positions

    handler_bw = space.add_collision_handler(1, 2)
    handler_bw.begin = on_collision_ball_wall
    handler_bw.data["collisions"] = collisions
    handler_bw.data["last_positions"] = last_positions

    handler_bp = space.add_collision_handler(1, 3)  
    handler_bp.begin = on_collision_ball_pocket

    cue_ball, remaining_balls = get_cue_ball(pool_balls)
    pool_balls = remaining_balls
    cue_ball_pos_start = (cue_ball.x_cord, cue_ball.y_cord )

    balls = []
    for pb in pool_balls:
        x = pb.x_cord
        y = pb.y_cord
        color = pb.color

        ball = SimulatedBall(x, y, int(ball_radius), color, velocity=(0,0))
        balls.append(ball)

    # Random cue ball velocity if not specified
    speed = random.uniform(150, 220)
    vx, vy = pymunk.Vec2d(speed, 0).rotated(math.radians(cue_angle))
    
    cue = SimulatedBall(
        cue_ball.x_cord, 
        cue_ball.y_cord, 
        int(ball_radius), 
        (255, 255, 255), 
        pymunk.Vec2d(vx, vy)
    )
    balls.append(cue)

    pockets = create_pockets(WIDTH, HEIGHT)

    tempfile_svg_name = run_game(balls, screen, clock, pockets, show_simulation, WIDTH, HEIGHT)
    return tempfile_svg_name, cue_ball_pos_start
