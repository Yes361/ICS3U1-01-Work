import pgzrun
import os

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 600
HEIGHT = 600

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
    ball.dx = 5 if paddle2.score > paddle1.score else -5
    ball.dy = 1

# Update - Handle ongoing input, update positions, check interactions
def update():
    
    if keyboard[keys.S]:
        paddle1.y += 5
    if keyboard[keys.W]:
        paddle1.y -= 5
    if keyboard[keys.DOWN]:
        paddle2.y += 5
    if keyboard[keys.UP]:
        paddle2.y -= 5
    
    ball.x += ball.dx
    ball.y += ball.dy    
    
    if ball.colliderect(paddle1) or ball.colliderect(paddle2):
        ball.dx *= -1

    if ball.x < paddle1.x:
        paddle2.score += 1
        reset_ball()
    elif ball.x > paddle2.x:
        paddle1.score += 1
        reset_ball()
    
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
