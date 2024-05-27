import pgzrun
from pgzero.builtins import Actor, clock, animate, sounds, keys, keyboard
from pgzhelper import * 
import random
import os

# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 800
HEIGHT = 600
ALIENS_PER_ROW = 9

# Initialize Global Variables
score = 0
lives = 3
difficulty = 0
is_playing = False
has_game_started = False

play_again = Rect(((800 * 1 / 3, 200), (800 / 3, 200)))

# Initialize primary Actors
player = Actor('playership2_orange')
player.pos = (WIDTH // 2, HEIGHT - 50)
player.scale = 0.5 #resizing sprite to something more reasonable

ufo = Actor('enemygreen1', pos=(50, 50))
ufo.points = 100

aliens = []
alien_bullets = []
furthest_alien = None
alien_direction = 20
max_height = 450

alien_color_index = {
    'green': 150,
    'black': 200,
    'blue': 250,
    'red': 300
}

def set_ufo():
    ufo.right = 0

shields = []
def spawn_shield(pos):
    shield = Actor('shield3', pos=pos)
    shield.level = 3
    shields.append(shield)

def draw_row_aliens(type, y, points):    
    global aliens
    for x in range(ALIENS_PER_ROW):
        a = Actor(type)
        a.scale = 0.5
        xc = (WIDTH - ALIENS_PER_ROW * 60) // 2 + (x * 60) + 30 # A little math to center the row
        a.center = (xc, y)
        a.points = points
        aliens.append(a)
        
def draw_all_aliens(difficulty):
    last_y = 100
    for i in range(difficulty):
        color = random.choice(['green', 'red', 'blue', 'black'])
        type = random.randint(1, 5)
        draw_row_aliens(f'enemy{color}{type}', last_y, points=alien_color_index[color])
        last_y += 50

def determine_direction():
    global aliens, alien_direction
    for alien in aliens:
        if alien_direction < 0 and alien.left < 50:
            return True
        if alien_direction > 0 and alien.right > 750:
            return True
    return False


def spawn_alien_bullet(type, pos):
    alien_bullet = Actor(type, pos=pos)
    alien_bullets.append(alien_bullet)

def alien_shoot():
    global aliens, lives
    if len(aliens) == 0:
        lives += 1
        draw_all_aliens(difficulty)
        
    alien = random.choice(aliens)
    if random.random() < 1:
        spawn_alien_bullet('laserblue07', alien.pos)

def move_aliens():
    global alien_direction, aliens
    
    if direction_change := determine_direction():
        alien_direction *= -1
        if alien_direction < 0:
            alien_direction -= 2
        else:
            alien_direction += 2
    
    below_max_height = False
    for alien in aliens:
        if direction_change:
            alien.y += 50
            below_max_height |= alien.bottom > max_height
        else:
            alien.x += alien_direction
    
    if below_max_height:
        handle_lose_condition()
        return
    
    alien_shoot()
        
def damage_shield(alien_bullet):
    for idx, shield in enumerate(shields):
        if not shield.colliderect(alien_bullet):
            continue
        
        shield.level -= 1
        if shield.level <= 0:
            shields.pop(idx)
            return True
        
        shield.image = f'shield{shield.level}'
        return True
    return False

def handle_alien_bullets():
    global lives, is_playing
    for idx, alien_bullet in enumerate(alien_bullets):
        alien_bullet.y += 5
        
        if damage_shield(alien_bullet):
            alien_bullets.pop(idx)
        
        if alien_bullet.colliderect(player):
            alien_bullets.pop(idx)
            lives -= 1
            
            if lives <= 0:
                handle_lose_condition()
                
        if alien_bullet.top > HEIGHT:
            alien_bullets.pop(idx)
            
def handle_player_bullets():
    global bullet, score
    if ufo.colliderect(bullet):
            ufo.left = WIDTH
            score += ufo.points

    bullet.y -= 5        
    for idx, alien in enumerate(aliens):
        if bullet.colliderect(alien):
            aliens.pop(idx)
            score += alien.points
            bullet = None
            return

    if bullet and bullet.bottom < 0:
        bullet = None

def handle_lose_condition():
    global is_playing, bullet
    is_playing = False
    clock.unschedule(move_aliens)
    alien_bullets.clear()
    bullet = None

def reset_game():
    global lives, score, is_playing, difficulty, alien_direction
    alien_direction = 20
    is_playing = True
    lives = 3
    score = 0
    difficulty = 1
    aliens.clear()
    draw_all_aliens(difficulty)
    clock.schedule_interval(move_aliens, 1)
    
    shields.clear()
    spawn_shield((100, 500))
    spawn_shield((400, 500))
    spawn_shield((700, 500))
    
    set_ufo()

def draw_game_screen():
    if not is_playing:
        screen.draw.filled_rect(play_again, (0, 0, 0))
        screen.draw.rect(play_again, (255, 255, 255))
        screen.draw.text('play moron', center=(400, 300))
        if has_game_started:
            screen.draw.text(f'HIGHSCORE: {score}', center=(400, 250))

bullet = None

# Event Handlers - Handle one-time input
def on_mouse_down(pos, button): 
    global has_game_started, is_playing
    if play_again.collidepoint(pos) and not is_playing:
        reset_game()
        has_game_started = True
        
def on_key_down(key, unicode):
    global bullet, is_playing
    
    if key == keys.SPACE and bullet == None and is_playing:
        bullet = Actor('laserblue07', player.pos)

# Update - Handle ongoing input, update positions, check interactions
def update():
    global bullet, is_playing, score
    
    if not is_playing:
        return
    
    if (keyboard[keys.LEFT] or keyboard[keys.A]) and player.left > 0:
        player.x -= 5
    if (keyboard[keys.RIGHT] or keyboard[keys.D]) and player.right < WIDTH:
        player.x += 5
        
    if bullet != None:
        handle_player_bullets()
            
    handle_alien_bullets()
        
    if ufo.left < WIDTH:
        ufo.x += 1
    else:
        clock.schedule(set_ufo, 1)
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
    screen.draw.text(f'{lives}', (750, 50))


# Setup, Scheduling, and Go:
pgzrun.go()
