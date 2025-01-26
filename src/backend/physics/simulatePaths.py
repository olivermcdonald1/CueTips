import pymunk
import pygame
import math
import random
from CueBall import CueBall


space = pymunk.Space() # Simulation space
space.gravity = (0, 0) # No gravity

table_height = 800
table_width = 600
screen = pygame.display.set_mode((table_height, table_width)) 
clock = pygame.time.Clock()

class SimulatedBall:
    def __init__(self, x, y, radius, color, velocity):
        self.radius = radius
        self.color = color
        self.velocity = velocity  # Initial velocity (in a direction)
        self.body = pymunk.Body(mass=1, movement=pymunk.moment_for_circle(mass=1, radius=radius))
        self.body.position = (x, y)
        
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
        
def run_game(balls, ball_radius):
    while running:
        # Handle events (like closing the window)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        space.step(1/50.0)  # 1/50th of a second step

        # Clear screen
        screen.fill((0, 0, 0))

        # Draw the balls
        for ball in balls:
            x, y = int(ball.position.x), int(ball.position.y)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), ball_radius)

        pygame.display.flip() # Update display
        clock.tick(50) # Cap the frame rate


def createBalls(pool_balls, ball_radius):
    simulated_balls = []
    for pool_ball in pool_balls:
       simulated_ball = SimulatedBall(
           x=pool_ball.x_cord,
           y=pool_ball.y_cord,
           color=pool_ball.color,
           radius=ball_radius
       ) 
       simulated_balls.append(simulated_ball)
    
    return simulated_balls
    
def simulatePaths(pool_balls, cue_ball, wall_cords, ball_radius):
    top_cords, bottom_cords, right_cords, left_cords = wall_cords
    
    createBorders(top_cords, bottom_cords, right_cords, left_cords)
    
    simulated_balls = createBalls(pool_balls, ball_radius)
    run_game(simulated_balls, ball_radius, cue_ball)
   
    
if __name__ == '__main__':
    angle = random.uniform(0, 2 * math.pi)
    
    # Random speed between 50 and 150
    speed = random.uniform(50, 150)

    # Create the initial velocity vector (speed, angle)
    velocity = pymunk.Vec2d(speed, 0).rotated(angle)
    cue_ball = CueBall(200,200,)
    
    simulatePaths(pool_balls, cue_ball, wall_cords, ball_radius)