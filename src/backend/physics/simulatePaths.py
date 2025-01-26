import sys
import math
import random
import pygame
import pymunk
import svgwrite

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


def save_paths_as_svg(collisions, filename="ball_paths.svg"):
   

    
    dwg = svgwrite.Drawing(filename, profile='tiny', size=(400, 800))

    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='rgb(38, 141, 44)'))

    for start, end, color in collisions:
        svg_color = f'rgb({color[0]},{color[1]},{color[2]})'
        dwg.add(dwg.line(
            start=(start[0], start[1]),
            end=(end[0], end[1]),
            stroke=svg_color,
            stroke_width=2
        ))

    dwg.save()

    
def create_borders():
    WIDTH, HEIGHT = 400, 800
    walls = [
        pymunk.Segment(space.static_body, (0,0),     (WIDTH,0),     5),  # top
        pymunk.Segment(space.static_body, (0,HEIGHT),(WIDTH,HEIGHT),5),  # bottom
        pymunk.Segment(space.static_body, (0,0),     (0,HEIGHT),    5),  # left
        pymunk.Segment(space.static_body, (WIDTH,0), (WIDTH,HEIGHT),5),  # right
    ]
    for wall in walls:
        wall.friction = 0.14
        wall.elasticity = 0.9
        wall.collision_type = 2
        space.add(wall)

def create_pockets():
    """Create 6 pockets for the pool table with visual outlines."""
    WIDTH, HEIGHT = 400, 800
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

def run_game(balls, screen, clock, cue_angle=90):
    running = True
    friction_coefficient = 0.7  #

    pockets = create_pockets()
    cue_ball = next((b for b in balls if b.color == (255, 255, 255)), None)
    if not cue_ball:
        raise ValueError("Cue ball is required for the simulation")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Apply velocity to the cue ball in the direction of the provided angle when stationary
        if cue_ball.body.velocity.length == 0 and cue_angle is not None:
            speed = 200  # Set the desired speed of the cue ball
            cue_ball.body.velocity = (
                speed * math.cos(cue_angle),
                speed * math.sin(cue_angle)
            )

        for ball in balls:
            velocity = ball.body.velocity
            ball.body.velocity = calculate_deceleration((velocity.x, velocity.y), friction_coefficient, 1/50.0)

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
        clock.tick(50)

    # Save the collisions as an SVG when the simulation ends
    save_paths_as_svg(collisions)

    pygame.quit()
    sys.exit()


# Add this modification to save the paths to an SVG file whenever the simulation ends.
# The saved SVG can then be embedded into a website using standard HTML <img> tags or <object> tags.



def main(pool_balls, cue_ball=None, wall_cords=None, ball_radius=15):
    global collisions, last_positions
    collisions = []
    last_positions = {}

    pygame.init()
    WIDTH, HEIGHT = 400, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    create_borders()

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

    balls = []
    for pb in pool_balls:
        x = pb.x_cord
        y = pb.y_cord
        color = pb.color

        ball = SimulatedBall(x, y, int(ball_radius), color, velocity=(0,0))
        balls.append(ball)

    if cue_ball is None:
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(150, 220)
        vx, vy = pymunk.Vec2d(speed, 0).rotated(angle)
        cue = SimulatedBall(WIDTH/2, HEIGHT/2, int(ball_radius), (255,255,255), (vx, vy))
        balls.append(cue)
    else:
        pass

    run_game(balls, screen, clock)
