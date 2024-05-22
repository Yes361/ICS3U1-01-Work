import pgzrun
import pygame
import os
import random 

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 600
HEIGHT = 600
play = False
time_between_movements = 3

# Global Variables
score = 0
lives = 10

# Initialize primary Actors
alien = Actor('alien_front', (WIDTH//2, HEIGHT//2))
alien.walking_state = 'alien_walk1'

def set_alien_hurt():
    global score
    alien.image = 'alien_hit'
    clock.schedule_unique(lambda: set_alien_normal('alien_front'), 1.0)
    
def set_alien_normal(state): 
    alien.image = state
    
def alternate_walking_animation():
    alien.walking_state = 'alien_walk1' if alien.walking_state == 'alien_walk2' else 'alien_walk2'
    alien.image = alien.walking_state
    
def move_alien():
    global play, time_between_movements
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    
    if play:
        alternate_walking_animation()
        animate(alien, pos=(x, y), on_finished=lambda: set_alien_normal('alien_stand'))
        clock.schedule(move_alien, time_between_movements)
        if time_between_movements > 0.1:
            time_between_movements -= 0.05
    
    
# Mouse and Keyboard Events

def on_mouse_down(pos, button):
    global lives, score, play
    
    if play and alien.image != 'alien_hit':
        if alien.collidepoint(pos):
            set_alien_hurt()
            score += 1
            # TODO: Play a sound on hit, and increase the player's score.
            sounds.laser_000.play()
        else:
            sounds.laser_001.play()
            lives -= 1
            if lives <= 0:
                clock.unschedule(move_alien)
                return
            
def on_key_down(key):
    global play
    if key == keys.SPACE and not play:
        play = True
        move_alien()


# Update - Handle ongoing input, update positions, check interactions
def update():
    pass
    
# Draw - Draw each Actor, and any other UI elements
def draw():
    global play
    screen.clear()
    screen.blit('colored_shroom.png', (0, 0))
    alien.draw()
    
    #TODO: Draw the player's score and lives on the screen.
    screen.draw.text(f'{score}', center=(50, 50))
    screen.draw.text(f'{lives}', center=(WIDTH - 50, 50))
    
    #TODO: Display a Game Over message when the player's lives reach zero.
    if lives <= 0:
        screen.draw.text('GAME OVER', center=(WIDTH / 2, HEIGHT / 2))
        play = False
    
pgzrun.go()
