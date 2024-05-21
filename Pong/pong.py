import pgzrun
import random
from math import sin, cos, pi
import os

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 600
HEIGHT = 600
speed_increase = 0.05
play = True

# Initialize primary Actors
paddle1 = Actor('paddle_blue', center=(0, 0))
paddle1.score = 0
paddle1.angle = 90

paddle2 = Actor('paddle_red', center=(WIDTH, 0))
paddle2.score = 0
paddle2.angle = 90

ball = Actor('ball_grey')

def reset_ball():
    ball.pos = (300, 300)
    direction = random.randint(0, 360) * pi / 180
    ball.dx = cos(direction) * 5
    ball.dy = sin(direction) * 5
    
def switch_game_state():
    pass

# Update - Handle ongoing input, update positions, check interactions
def update():
    # Key board input
    if play:
        if keyboard[keys.S]:
            paddle1.y += 5
            if paddle1.bottom > HEIGHT:
                paddle1.y -= 5
        if keyboard[keys.W]:
            paddle1.y -= 5
            if paddle1.top < 0:
                paddle1.y += 5
        if keyboard[keys.DOWN]:
            paddle2.y += 5
            if paddle2.bottom > HEIGHT:
                paddle2.y -= 5
        if keyboard[keys.UP]:
            paddle2.y -= 5
            if paddle2.top < 0:
                paddle2.y += 5
        
        # Moving the ball
        ball.x += ball.dx
        ball.y += ball.dy    
        
        if ball.colliderect(paddle1) or ball.colliderect(paddle2):
            ball.dy *= 1 + speed_increase
            ball.dx *= -1 - speed_increase
            sounds.impactmetal.play()
            

        # Change score based on which side the ball makes contact with
        if ball.left < 0:
            paddle2.score += 1
            sounds.laserretro.play()
            reset_ball()
        elif ball.right > WIDTH:
            paddle1.score += 1
            sounds.laserretro.play()
            reset_ball()
        
        # Handle collisions with the top and bottom
        if ball.top < 0 or ball.bottom > HEIGHT:
            ball.dy *= -1

# Draw - Draw each Actor, and any other UI elements
def draw():
    screen.clear()
    paddle1.draw()
    paddle2.draw()
    ball.draw()
    
    screen.draw.text(f'{paddle1.score}', (50, 50))
    screen.draw.text(f'{paddle2.score}', (WIDTH - 50, 50))
    
# Setup and Go:
reset_ball()

pgzrun.go()
