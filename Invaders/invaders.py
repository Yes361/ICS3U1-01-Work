"""
Title: Space Invaders
Author: Raiyan Islam
Date: 2024-05-31
Description:
Space Invaders is a classic arcade game. You control a laser cannon, 
moving it horizontally across the screen, evading the waves of alien invaders.
The objective is to elimate all the aliens before they reach the bottom.
"""

from pgzero.builtins import Actor, clock, sounds, keys, keyboard, Rect
from typing import List
import pgzrun
from pgzhelper import * 
import random
import os

### DEFINITION
# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 800
HEIGHT = 600

# Constants
ALIENS_PER_ROW = 9
ALIEN_VERTICAL_SPACING = 50
BULLET_PER_TICK_CHANCE = 0.5
MIN_MOVEMENT_DELAY = 0.5
ALIEN_DEFAULT_DELAY = 1

# Initialize Global Variables
score = 0
lives = 3
game_level = 0
game_active = False
game_started = False
game_paused = False

# Initialize primary Actors
player = Actor('playership2_orange', pos=(WIDTH // 2, HEIGHT - 50))
player.death_frame = 0 # Custom Property to handle death animation
player.scale = 0.5

# UFO Actor
ufo = Actor('enemygreen1', pos=(-50, 50)) # Spawn off-screen
ufo.points = 100
ufo.is_waiting = False
ufo.direction = 1

# Actor Lists
aliens: List[Actor] = []
alien_bullets: List[Actor] = []
top_row_aliens: List[Actor] = [] # Contains the first aliens in each row
shields: List[Actor] = []

# Alien Variables
alien_max_height = 450 # Max height
alien_direction = 20
alien_delay = 1 # Movement delay
alien_delay_rate = 0.05 # Rate at which the movement decreases


# Game Over/Start Screen Variables
view_box = Rect(((WIDTH / 3, HEIGHT / 3), (WIDTH / 3, HEIGHT / 3)))
death_message = ''

bullet = None

### HELPER FUNCTIONS

# Returns a random image asset based on the prefix, a list of colors, and the min-max index
def generate_random_tag(prefix, colors, minIndex=0, maxIndex=0):
    color = random.choice(colors)
    
    # Handle image assets with index
    if minIndex != maxIndex:
        index = random.randint(minIndex, maxIndex)
        digits = len(str(maxIndex)) # get amount of digits
        return f'{prefix}{color}{index:0{digits}d}', color, index
    return f'{prefix}{color}', color    

# Set UFO properties while it's offscreen
def set_ufo():
    tag, _ = generate_random_tag('ufo', ['blue', 'green', 'red', 'yellow'])
    ufo.points = random.randint(5, 10) * 100
    ufo.image = tag
    ufo.scale = 0.5
    ufo.direction *= -1
    if ufo.direction < 0:
        ufo.left = WIDTH
    else:
        ufo.right = 0
    
# Move the UFO and schedule when it should appear on the screen again
def move_ufo():
    # Move the UFO if it's on-screen
    if (ufo.right > 0 and ufo.direction < 0) or (ufo.left < WIDTH and ufo.direction > 0):
        ufo.x += ufo.direction
        ufo.is_waiting = False
    elif not ufo.is_waiting: # Make sure it's scheduled only once
        next_time = random.randint(10, 20)
        clock.schedule(set_ufo, next_time)
        ufo.is_waiting = True    

# Spawn a Shield with a starting level of 3 at pos
def spawn_shield(pos):
    shield = Actor('shield3', pos=pos)
    shield.level = 3
    shields.append(shield)

# Draws a row of aliens of a certain type at Y that are worth a certain amount of points once shot
def draw_row_aliens(type, y, points):
    global aliens
    row = []
    for idx in range(ALIENS_PER_ROW):
        a = Actor(type)
        a.scale = 0.5
        xc = (WIDTH - ALIENS_PER_ROW * 60) // 2 + (idx * 60) + 30 # A little math to center the row
        
        a.center = (xc, y)
        a.points = points
        a.row = idx # Keep track of which row this alien belongs to
        
        aliens.append(a)
        row.append(a)
    return row
        
# Draws all the Aliens based on the current level/difficulty
def draw_all_aliens(difficulty=1, y=100):
    global aliens, top_row_aliens
    
    aliens.clear()
    
    # TODO: change alien points
    alien_color_index = {
        'green': 50,
        'black': 100,
        'blue': 200,
        'red': 250
    }
    
    # TODO: figure out a meaningful progression system
    rows = min(difficulty, 4) # Cap alien rows at 4
    for idx in range(rows):
        tag, color, _ = generate_random_tag('enemy', ['green', 'red', 'blue', 'black'], 1, 5)
        
        y_level = y + ALIEN_VERTICAL_SPACING * idx
        points = alien_color_index[color] + (rows - idx) * 50 # Score is based on color and row
        alien_row = draw_row_aliens(tag, y_level, points)
        
        if idx == 0:
            top_row_aliens = alien_row # Set the top row of aliens to the first row

# Update the highest alien in top_row_aliens for a specific row
def find_highest_alien(row):
    global top_row_aliens
    
    current_height = HEIGHT
    current_alien = None
    for alien in aliens:
        # Change current_alien, and current_height if we found an alien that is further up
        if alien.row == row and alien.y < current_height: 
            current_alien = alien
            current_height = alien.y
            
    top_row_aliens[row] = current_alien
    return current_alien

# Returns True if the aliens should change direction
# The params, left and right, represent how far the aliens can go
# in the x-axis
def determine_direction(left = 50, right = WIDTH - 50):
    global aliens, alien_direction
    for alien in aliens:
        if (alien_direction < 0 and alien.left < left) or (alien_direction > 0 and alien.right > right):
            return True
    return False

# Spawn a random bullet at pos
def spawn_bullet(pos):
    tag, _, _ = generate_random_tag('laser', ['blue', 'green', 'red'], 1, 16)
    bullet = Actor(tag, pos)
    bullet.scale = 0.5
    return bullet

def spawn_alien_bullet():
    global aliens, alien_bullets, top_row_aliens
    
    # Filter top_row_alien as it may contain null values
    filtered_alien_list = list(filter(lambda x: x != None, top_row_aliens)) 
    alien = random.choice(filtered_alien_list)
    
    bullet = spawn_bullet(alien.pos)
    alien_bullets.append(bullet)
    return bullet

# Handle all Alien movement
def move_alien():
    global alien_direction, alien_delay, aliens
    direction_change = determine_direction()
    
    if direction_change:
        alien_direction *= -1 # Change directions if required
        
        # Speed up the aliens
        if alien_delay < MIN_MOVEMENT_DELAY: 
            alien_delay -= alien_delay_rate
    
    below_max_height = False
    for alien in aliens:
        # If we've changed direction, move downwards
        if direction_change:
            alien.y += ALIEN_VERTICAL_SPACING
            below_max_height |= alien.bottom > alien_max_height
        else:
            alien.x += alien_direction
    
    # If the aliens are above a certain y threshold, trigger the lost condition
    if below_max_height:
        handle_lose_condition()

def next_level():
    global lives, game_level, alien_delay
    
    lives += 1
    game_level += 1
    alien_delay = ALIEN_DEFAULT_DELAY
    draw_all_aliens(game_level)

# Manages alien bullet spawning and movement
def manage_alien_behavior():
    global aliens, alien_delay
    
    if not is_game_running():
        return
    
    # Increment lives counter if there are no aliens remaining
    if len(aliens) == 0:
        next_level()
        
    move_alien()
    
    # Random chance of a bullet spawning
    if random.random() < BULLET_PER_TICK_CHANCE:
        spawn_alien_bullet()
    
    clock.schedule(manage_alien_behavior, alien_delay)
    
# Returns True if a bullet hits the shield, and "degrades" the shield
def damage_shield(alien_bullet):
    for shield in shields:
        if not shield.colliderect(alien_bullet):
            continue
        
        # Degrade the shield, and update the image
        shield.level -= 1
        if shield.level <= 0:
            shields.remove(shield)
        else:
            shield.image = f'shield{shield.level}'
        return True
    return False

# Death animation, pauses the game if its running
def animate_death():
    global player, game_active, game_paused
    if player.death_frame > 2:
        
        game_paused = False
        player.image = 'playership2_orange'
        player.scale = 0.5
        player.death_frame = 0
        
        # Resume alien movement
        clock.schedule_unique(manage_alien_behavior, alien_delay)
    else:
        game_paused = True
        player.death_frame += 1
        player.image = f'star{player.death_frame}'
        
        clock.schedule_unique(animate_death, 0.3)

# Handles interaction of alien bullets with other objects
def handle_alien_bullets():
    global lives, alien_bullets
    for alien_bullet in alien_bullets:
        alien_bullet.y += 5
        
        if damage_shield(alien_bullet):
            alien_bullets.remove(alien_bullet)
            sounds.forcefield_002.play()
        
        elif alien_bullet.top > HEIGHT:
            alien_bullets.remove(alien_bullet)
            
        elif alien_bullet.colliderect(player):
            alien_bullets.remove(alien_bullet)
            sounds.lowfrequency_explosion_000.play()
            
            lives -= 1
            if lives <= 0:
                handle_lose_condition()
            else:
                animate_death()
            
# Handles interaction of player bullets with other objects
def handle_player_bullets():
    global aliens, bullet, score
    bullet.y -= 5   
         
    if ufo.colliderect(bullet):
        # Move it offscreen/skip to the end
        if ufo.direction > 0:
            ufo.left = WIDTH 
        else:
            ufo.right = 0
        
        score += ufo.points
        bullet = None
        return
    
    if bullet.bottom < 0:
        bullet = None
        return
    
    # Find which alien is shot
    for alien in aliens:
        if not bullet.colliderect(alien):
            continue
        
        aliens.remove(alien)
        find_highest_alien(alien.row) # Update the first alien in each row
        
        sounds.impactmetal_003.play()
        score += alien.points # Add the alien points to the score
        bullet = None
        break

# Lose Condition
def handle_lose_condition(msg):
    global game_active, game_paused, bullet
    game_active = False
    game_paused = False
    bullet = None
    
    death_message = msg
    
    alien_bullets.clear()
    player.image = 'star3'
    sounds.thrusterfire_004.play()
    clock.unschedule(manage_alien_behavior)

# Resets the game for the next session
def reset_game():
    global lives, score, game_active, game_paused, game_level, alien_direction, alien_delay
    alien_direction = 20
    game_active = True
    game_paused = False
    lives = 3
    score = 0
    game_level = 1
    alien_delay = 1
    draw_all_aliens()
    
    player.image = 'playership2_orange'
    player.scale = 0.5
    
    shields.clear()
    spawn_shield((100, 500))
    spawn_shield((400, 500))
    spawn_shield((700, 500))
    set_ufo()
    
    clock.schedule(manage_alien_behavior, alien_delay)
    
# Returns True if the game is running and not paused
def is_game_running():
    return game_active and not game_paused

# Draws the start game/game over screen
def draw_game_screen():
    if not game_active:
        screen.draw.filled_rect(view_box, (0, 0, 0))
        screen.draw.rect(view_box, (255, 255, 255))
        screen.draw.text('Click this box to play', center=(400, 280))
        screen.draw.text('Controls: Arrow keys to move', center=(400, 320))
        screen.draw.text('Space to Shoot', center=(400, 340))
        if game_started:
            screen.draw.text(f'HIGHSCORE: {score}', center=(400, 250))

### Event Handlers

def on_mouse_down(pos, button): 
    global game_started, game_active
    if view_box.collidepoint(pos) and not is_game_running():
        reset_game()
        game_started = True
        
def on_key_down(key, unicode):
    global bullet, game_active    
    
    # Spawn bullet
    if key == keys.SPACE and bullet == None and is_game_running():
        bullet = Actor('laserblue07', player.pos)
        sounds.lasersmall_000.play()

# Update - Handle ongoing input, update positions, check interactions
def update(dt):
    global bullet, game_active, score    
    
    # Don't run anything if the game isn't active
    if not is_game_running():
        return
    
    # Player Controls
    if (keyboard[keys.LEFT] or keyboard[keys.A]) and player.left > 0:
        player.x -= 5
    if (keyboard[keys.RIGHT] or keyboard[keys.D]) and player.right < WIDTH:
        player.x += 5
        
    if bullet != None:
        handle_player_bullets()
            
    handle_alien_bullets()
    move_ufo()

# Draw - Draw each Actor, and any other UI elements
def draw():
    screen.clear()
    
    for alien in aliens:
        alien.draw()
        
    for alien_bullet in alien_bullets:
        alien_bullet.draw()
        
    for shield in shields:
        shield.draw()
        
    if bullet != None:
        bullet.draw()
    
    player.draw()
    ufo.draw()
    
    draw_game_screen()
    
    screen.draw.text(f'{score}', (50, 50))
    screen.draw.text(f'{lives}', (WIDTH - 50, 50))

pgzrun.go()