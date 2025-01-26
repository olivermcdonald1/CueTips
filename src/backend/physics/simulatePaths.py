import sys
import math
import random
import pygame
import pymunk


space = pymunk.Space()
space.gravity = (0, 0)


collisions = []
last_positions = {}


def on_collision_ball_ball(arbiter, space, data):
    shape_a, shape_b = arbiter.shapes

    for shape in (shape_a, shape_b):
        if shape.collision_type == 1:  # it's a ball
            current_pos = shape.body.position
            start_pos = data["last_positions"][shape]  
            end_pos = (current_pos.x, current_pos.y)
            
           
            data["collisions"].append((start_pos, end_pos))
            
      
            data["last_positions"][shape] = end_pos

    return True

def on_collision_ball_wall(arbiter, space, data):
    shape_a, shape_b = arbiter.shapes

    if shape_a.collision_type == 1:
        ball_shape = shape_a
    else:
        ball_shape = shape_b

    current_pos = ball_shape.body.position
    start_pos = data["last_positions"][ball_shape]
    end_pos = (current_pos.x, current_pos.y)

    data["collisions"].append((start_pos, end_pos))
    data["last_positions"][ball_shape] = end_pos

    return True


class SimulatedBall:
    def __init__(self, x, y, radius, color, velocity=(0, 0)):
        """
        x, y: positions
        radius: ball radius
        color: (R,G,B)
        velocity: (vx, vy)
        """
        self.radius = radius
        self.color = color

      
        self.body = pymunk.Body(mass=1, moment=pymunk.moment_for_circle(1, 0, radius))
        self.body.position = (x, y)
        self.body.velocity = velocity

        
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.06
        self.shape.elasticity = 0.9
        self.shape.collision_type = 1  

        space.add(self.body, self.shape)

    
        last_positions[self.shape] = (x, y)

    def draw(self, screen):
        pos = self.body.position
        pygame.draw.circle(screen, self.color, (int(pos.x), int(pos.y)), self.radius)

#
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
        wall.collision_type = 2  # Mark as "wall"
        space.add(wall)


def run_game(balls, screen, clock):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Step physics
        space.step(1/50.0)

        # Clear screen
        screen.fill((0, 0, 0))

        # Draw the balls
        for b in balls:
            b.draw(screen)

        # Draw red collision lines
        for line_seg in collisions:
            start, end = line_seg
            pygame.draw.line(screen, (255, 0, 0),
                             (int(start[0]), int(start[1])),
                             (int(end[0]), int(end[1])),
                             2)

        pygame.display.flip()
        clock.tick(50)

    pygame.quit()
    sys.exit()


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