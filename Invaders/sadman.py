import pgzrun, os, random
from pgzhelper import *



# Window Settings
os.environ['SDL_VIDEO_CENTERED'] = '1' #Forces window to be centered on screen.
WIDTH = 800
HEIGHT = 600
ALIENS_PER_ROW = 9

# Initialize Global Variables
score = 0
lives = 3

# keeps track of direction of movement
alien_direction = 0.5




### Initialize primary Actors
# Player
player= Actor('playership2_orange')
player.pos = (WIDTH // 2, HEIGHT - 50)
player.scale = 0.5 #resizing sprite to something more reasonable
# Player Bullet (checks whether it exists)
bullet = None

#UFO
ufo = Actor("ufoblue",)
ufo.scale *= 0.5
ufo.pos = (0, 50)
ufo.direction = 0
ufo.directon = 1
# Checks whether UFO has been scheduled
ufo.called = False

# Top row of aliens
top_row = []

#Aliens
aliens = []
alien_bullets = []





for x in range(ALIENS_PER_ROW):
    for y in range(4):

        a = Actor('enemygreen1')
        a.scale = 0.5
        xc = (WIDTH - ALIENS_PER_ROW * 60)//2 + (x * 60) + 30 # A little math to center the row
        # Chnages enemy image
        if y == 2:
            a.image = ("enemyblack1")
        if y == 1:
            a.image = ("enemyblue2")
        if y == 0:
            a.image = ("enemyred3")

        a.center = (xc, 100 + 50 * y)
        a.column = x
        aliens.append(a)

        # Adds the top aliens to a list
        if y == 0:
            top_row.append(a)


### Checks if alien hits wall
def alien_change():
    global alien_direction
    for alien in aliens:
        if alien.right > WIDTH and alien_direction > 0:
            return True
        if alien.left < 0 and alien_direction < 0:
            return True


# checks alien by seeing if there is a higher alien in the column
def check_alien(column):
    current_alien = None
    current_height = HEIGHT
    for alien in aliens:
        if alien.column == column and alien.y < current_height:
            current_alien = alien
            current_height = alien.y

    top_row[column] = (current_alien)


def alien_move():
    global alien_direction
    change = alien_change()

    if change == True:
        # Changes direction sideways
        alien_direction *= -1

    for alien in aliens:
        # Checks change
        if change == True:
            # moves everything down
            alien.y += 50

        # Moves alien
        else:
            alien.x += alien_direction


# spawns  alien bullet
def spawn_alien_bullet():
    global top_row
    print(len(top_row))
    for alien in top_row:
        if alien:
            if random.randint(0,5) == 0:
                # Alien Bullets
                alien_bullet = Actor("laserblue02")
                alien_bullet.scale *= 0.5
                alien_bullet.pos = alien.pos
                alien_bullets.append(alien_bullet)
                alien_bullet.y += 5




def ufo_change(): 	# raiyan hit the jutsu magic and made code work (its cuz 0 returns false)
    # Assigns direction
    if random.randint(0, 1)  == 1:
        ufo.direction = 2
    else:
        ufo.direction = -2

    if ufo.direction > 0:
        ufo.right = 0
    if ufo.direction < 0:
        ufo.left = WIDTH

def ufo_move():
    global ufo

    # Determinds whether to spawn UFO on left or right side of screen

    if ufo.direction > 0 and ufo.left < WIDTH:
        ufo.x += ufo.direction
        ufo.called = False

    elif ufo.direction < 0 and ufo.right > 0:
        ufo.x += ufo.direction
        ufo.called = False

    # schedules next UFO
    elif ufo.called == False :
        clock.schedule_unique(ufo_change, random.randint(10,15))
        ufo.called = True



# Event Handlers - Handle one-time input
# def on_mouse_down(pos, button):
# def on_mouse_up(pos, button):
# def on_mouse_move(pos, rel, buttons):
# def on_key_up(key, unicode):
# def on_music_end():

def on_key_down(key, unicode):
    global bullet

    if key == keys.SPACE and bullet == None:
        bullet = Actor('laserblue07', player.pos)
        sounds.laserlarge_004.play()



# Update - Handle ongoing input, update positions, check interactions
def update():
    global bullet, score

    if keyboard[keys.LEFT] and player.left > 0:
        player.x -= 5
    if keyboard[keys.RIGHT] and player.right < WIDTH:
        player.x += 5

    if bullet != None:
        bullet.y -= 5
        if bullet.bottom < 0:
            bullet = None

        # Remves bullet if hits alien, removes alien, increases score
        for alien in aliens:
            if bullet and bullet.colliderect(alien):
                bullet = None
                aliens.remove(alien)

                check_alien(alien.column)

                # Increases points depending on alien
                if alien.image == "enemyblack1":
                    score += 20
                elif alien.image == "enemyblue2":
                    score += 30
                elif alien.image == "enemyred3":
                    score += 40
                else:
                    score += 10
                break

    for alien_bullet in alien_bullets:
        alien_bullet.y += 1



        # Gives points on if UFO hits
        if bullet and bullet.colliderect(ufo):
            bullet = None
            if ufo.direction > 0 :
                ufo.left = WIDTH
            else:
                ufo.right = 0
            score += 100


    ufo_move()
# Draw - Draw each Actor, and any other UI elements
def draw():
    screen.clear()

    for alien in aliens:
        alien.draw()

    if bullet != None:
        bullet.draw()

    player.draw()
    alien_move()
    for alien_bullet in alien_bullets:
        alien_bullet.draw()


    screen.draw.text(f"Score        {score}", (10, 15))
    screen.draw.text(f"Lives        {lives}", (WIDTH - 100, 15))

    # draws ufo
    ufo.draw()


# Setup, Scheduling, and Go:
ufo_change()
clock.schedule_interval(spawn_alien_bullet,1.5)
pgzrun.go()