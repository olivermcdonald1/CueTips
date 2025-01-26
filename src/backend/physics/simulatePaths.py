import pymunk
import pygame
import math
import random

space = pymunk.Space()  # Simulation space
space.gravity = (0, 0)  # No gravity



class SimulatedBall:
    def __init__(self, x, y, radius, color, velocity):
        self.radius = radius
        self.color = color
        self.body = pymunk.Body(mass=1, moment=pymunk.moment_for_circle(1, 0, radius))
        self.body.position = (x, y)
        self.body.velocity = velocity

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 0.06  # Pool balls have little friction, 0.03-0.08
        self.shape.elasticity = 0.9  # very elastic
        
        space.add(self.body, self.shape)
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.body.position.x), int(self.body.position.y)), self.radius)

def createBorders(top_cords, bottom_cords, right_cords, left_cords):
    walls = [
        pymunk.Segment(space.static_body, top_cords[0], top_cords[1], 5),  # top
        pymunk.Segment(space.static_body, bottom_cords[0], bottom_cords[1], 5),  # bottom
        pymunk.Segment(space.static_body, right_cords[0], right_cords[1], 5),  # right
        pymunk.Segment(space.static_body, left_cords[0], left_cords[1], 5),  # left
    ]
    
    for wall in walls:
        wall.friction = 0.14  # friction for walls, found online
        wall.elasticity = 0.9
        space.add(wall)
        
def run_game(balls, ball_radius, cue_ball, screen, clock):
    running = True
    while running:
        # Handle events (like closing the window)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        space.step(1/50.0)  # 1/50th of a second step

        # Clear screen
        screen.fill((0, 0, 0))

        # Draw the cue ball
        cue_ball.draw(screen)

        # Draw the other balls
        for ball in balls:
            ball.draw(screen)

        pygame.display.flip()  # Update display
        clock.tick(50)  # Cap the frame rate


def createBalls(pool_balls, ball_radius):
    simulated_balls = []
    for pool_ball in pool_balls:
        simulated_ball = SimulatedBall(
            x=pool_ball.x_cord,
            y=pool_ball.y_cord,
            color=pool_ball.color,
            radius=ball_radius,
            velocity=(0, 0)  # No velocity for the other balls initially
        ) 
        simulated_balls.append(simulated_ball)
    
    return simulated_balls
    
def simulatePaths(pool_balls, cue_ball, wall_cords, ball_radius):
    # Define borders
    top_cords = [(0, 0), (700, 0)] # Top wall (x1, y1) to (x2, y2)
    bottom_cords = [(0, 1000), (700, 5000)] # Bottom wall (x1, y1) to (x2, y2)
    left_cords = [(0, 0), (0, 1000)] # Left wall (x1, y1) to (x2, y2)
    right_cords = [(700, 0), (700, 5000)] # Right wall (x1, y1) to (x2, y2)

    table_height = bottom_cords[0][1] - top_cords[0][1]
    table_width = right_cords[0][0] - left_cords[0][0]
    print(table_height, table_width)
    screen = pygame.display.set_mode((table_height, table_width)) 
    clock = pygame.time.Clock()
    
    createBorders(top_cords, bottom_cords, right_cords, left_cords)

    # Create balls
    simulated_balls = createBalls(pool_balls, ball_radius)

    # Cue ball with random angle and speed
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(50, 150)
    velocity_vec = pymunk.Vec2d(speed, 0).rotated(angle)
    cue_ball = SimulatedBall(200, 200, ball_radius, (255, 255, 255), velocity_vec)

    # Start game simulation
    run_game(simulated_balls, ball_radius, cue_ball, screen, clock)
   
    paths = []  # Store paths of the balls for analysis (optional)
    
    return paths

class CueBall:
    def __init__(self, x_cord, y_cord, initial_speed_vector):
        self.x_cord = x_cord
        self.y_cord = y_cord
        self.initial_speed_vector = initial_speed_vector