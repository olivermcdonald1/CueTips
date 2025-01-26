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
       
        if shape.collision_type == 1:
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
    def __init__(self, x, y, radius, color, velocity=(0,0)):
      
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
        pygame.draw.circle(
            screen,
            self.color,
            (int(pos.x), int(pos.y)),
            self.radius
        )

def create_borders(top_cords, bottom_cords, right_cords, left_cords):
    """
    Each argument is ((x1,y1),(x2,y2)) for the table edge.
    We'll give these walls collision_type=2 so we can track ball-wall collisions.
    """
    walls = [
        pymunk.Segment(space.static_body, top_cords[0], top_cords[1], 5),
        pymunk.Segment(space.static_body, bottom_cords[0], bottom_cords[1], 5),
        pymunk.Segment(space.static_body, right_cords[0], right_cords[1], 5),
        pymunk.Segment(space.static_body, left_cords[0], left_cords[1], 5),
    ]
    for wall in walls:
        wall.friction = 0.14
        wall.elasticity = 0.9
        wall.collision_type = 2
        space.add(wall)


def run_game(balls, screen, clock):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        space.step(1/50.0)

      
        screen.fill((0,0,0))

      
        for b in balls:
            b.draw(screen)

        for line_seg in collisions:
            start, end = line_seg
            pygame.draw.line(
                screen, (255, 0, 0),
                (int(start[0]), int(start[1])),
                (int(end[0]), int(end[1])),
                2
            )

        pygame.display.flip()
        clock.tick(50)

    pygame.quit()
    sys.exit()


def main():
    pygame.init()
    
    # Table is 400 wide, 800 tall
    WIDTH, HEIGHT = 400, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Create borders (top, bottom, left, right)
    top_cords    = ((0, 0), (WIDTH, 0))
    bottom_cords = ((0, HEIGHT), (WIDTH, HEIGHT))
    left_cords   = ((0, 0), (0, HEIGHT))
    right_cords  = ((WIDTH, 0), (WIDTH, HEIGHT))
    create_borders(top_cords, bottom_cords, right_cords, left_cords)


    handler_ball_ball = space.add_collision_handler(1, 1)
    handler_ball_ball.begin = on_collision_ball_ball
    handler_ball_ball.data["collisions"] = collisions
    handler_ball_ball.data["last_positions"] = last_positions

    handler_ball_wall = space.add_collision_handler(1, 2)
    handler_ball_wall.begin = on_collision_ball_wall
    handler_ball_wall.data["collisions"] = collisions
    handler_ball_wall.data["last_positions"] = last_positions

 
    balls = []

   
    angle = random.uniform(0, 2*math.pi)
    speed = random.uniform(200, 250)
    vx, vy = pymunk.Vec2d(speed, 0).rotated(angle)
    cue_ball = SimulatedBall(
        x=WIDTH/2, 
        y=HEIGHT/2,
        radius=15,
        color=(255, 255, 255),
        velocity=(vx, vy)
    )
    balls.append(cue_ball)

    for _ in range(4):
        x = random.randint(50, WIDTH-50)
        y = random.randint(50, HEIGHT-50)
        color = (random.randint(100,255), random.randint(100,255), random.randint(100,255))
        ball = SimulatedBall(x, y, 15, color)
        balls.append(ball)

    run_game(balls, screen, clock)


if __name__ == "__main__":
    main()