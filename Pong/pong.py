import pgzrun
import random
from math import sin, cos, pi
import os

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 600
HEIGHT = 600

# Global variables
margins = 100
speed_increase = 0.05
play = False
single_player_mode = True

# Initialize primary Actors
paddle1 = Actor('paddle_blue', center=(margins, 0))
paddle1.score = 0
paddle1.angle = 90

paddle2 = Actor('paddle_red', center=(WIDTH - margins, 0))
paddle2.score = 0
paddle2.angle = 90

ball = Actor('ball_grey')

def reset_ball():
    ball.pos = (300, 300)
    
    min_val, max_val = (-45, 45) if paddle1.score < paddle2.score else (135, 225)
    direction = random.randint(min_val, max_val) * pi / 180
    ball.dx = cos(direction) * 5
    ball.dy = sin(direction) * 5

# Enable replay and single player mode 
def on_key_down(key):
    global play, single_player_mode
    if not play:
        if key == keys.B:
            single_player_mode = not single_player_mode
    play = True

# Update - Handle ongoing input, update positions, check interactions
def update():
    global play
    # Key board input
    if play:
        if keyboard[keys.S]:
            paddle1.y += 5
            # Vertical constraint
            if paddle1.bottom > HEIGHT:
                paddle1.y -= 5
        if keyboard[keys.W]:
            paddle1.y -= 5
            if paddle1.top < 0:
                paddle1.y += 5
                
        if keyboard[keys.DOWN] and single_player_mode:
            paddle2.y += 5
            if paddle2.bottom > HEIGHT:
                paddle2.y -= 5
        if keyboard[keys.UP] and single_player_mode:
            paddle2.y -= 5
            if paddle2.top < 0:
                paddle2.y += 5
                
        # Single Player logic
        if not single_player_mode:
            paddle2.y = ball.y
        
        if ball.colliderect(paddle1):
            # change required to resolve collision
            dx = ball.x - paddle1.right
            dy = ball.y - paddle1.top
            # resolve collision (x/y axis) and change speed
            if abs(dx) < abs(dy):
                ball.x += dx
                ball.dx *= -1 - speed_increase
            else:
                ball.y += dy
                ball.dy *= -1 - speed_increase
            sounds.impactmetal.play()  
        elif ball.colliderect(paddle2):
            dx = ball.x - paddle2.left
            dy = ball.y - paddle2.top
            if abs(dx) < abs(dy):
                ball.x += dx
                ball.dx *= -1 - speed_increase
            else:
                ball.y += dy
                ball.dy *= -1 - speed_increase

            sounds.impactmetal.play()

        # Moving the ball
        ball.x += ball.dx
        ball.y += ball.dy

        # Change score based on which side the ball makes contact with
        hit = False
        if ball.left < 0:
            paddle2.score += 1
            hit = True
        elif ball.right > WIDTH:
            paddle1.score += 1
            hit = True
        
        # Handle ball flying off-screen
        if hit:
            sounds.laserretro.play()
            play = False
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
    screen.draw.text(f'Press B when the ball is reset to change to single-player mode', center=(WIDTH / 2, HEIGHT - 50))
    
# Setup and Go:
reset_ball()

pgzrun.go()