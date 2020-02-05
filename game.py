import pygame
import os
import random
from os import path

# Sound effects from:
#   Ted Kerr
#   Gumichan01
#   Duckstruction
#   http://cubeengine.com/forum.php4?action=display_thread&thread_id=2164


# Center the game window
def centerWindow():
    x = 500
    y = 100
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)


img_dir = path.join(path.dirname(__file__), 'img')
sound_dir = path.join(path.dirname(__file__), 'sound')

# Set dimensions
WIDTH = 900
HEIGHT = 900
FPS = 120

# Set colours
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


# Center the window, initialise pygame and create window
centerWindow()

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroid")
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial')


# Spawn enemies
def spawn_regular_enemy():
    e = RegularEnemy()
    all_sprites.add(e)
    enemies.add(e)


def spawn_upgraded_enemy():
    e = UpdgradedEnemy()
    all_sprites.add(e)
    enemies.add(e)


def spawn_random_enemy():
    if random.uniform(0, 1) < 0.5:
        spawn_upgraded_enemy()
    else:
        spawn_regular_enemy()

# Draw health bar


def draw_health_bar(surface, x, y, health):
    if health < 0:
        health = 0
    BAR_LENGTH = 200
    BAR_HEIGHT = 20
    fill = (health/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

# Draw text, used for the score


def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


# Random number excluding a certain number, used to generate velocity that is not 0
def range_with_no_number(start, end, exclude):
    l = [i for i in range(start, end) if i != exclude]
    return random.choice(l)

# Player class


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = player_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 32
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.velocity = 0
        self.flycount = 0
        self.health = 100

    def update(self):
        self.velocity = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.velocity = -5
        if keystate[pygame.K_RIGHT]:
            self.velocity = 5
        self.rect.x += self.velocity
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        laser = PlayerLaser(self.rect.centerx, self.rect.top)
        all_sprites.add(laser)
        player_lasers.add(laser)
        laser_sound.play()

# Enemy class


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-20, 0)
        self.x_velocity = random.randrange(-2, 2)
        self.radius = 20

    def update(self):
        raise NotImplementedError("Must override method")

# Enemy child class


class RegularEnemy(Enemy):
    def __init__(self):
        self.image = regular_enemy_img
        self.image.set_colorkey(BLACK)
        super().__init__()
        self.firerate = 5
        self.y_velocity = random.randrange(3, 5)

    def update(self):
        self.rect.y += self.y_velocity
        self.rect.x += self.x_velocity
        if self.rect.top > HEIGHT + 10 or self.rect.left < -20 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-20, 0)
            self.x_velocity = range_with_no_number(-1, 2, 0)

# Enemy child class


class UpdgradedEnemy(Enemy):
    def __init__(self):
        self.image = upgraded_enemy_img
        self.image.set_colorkey(BLACK)
        super().__init__()
        self.firerate = 10
        self.y_velocity = random.randrange(1, 2)

    def update(self):
        self.rect.y += self.y_velocity
        self.rect.x += self.x_velocity
        if self.rect.top > HEIGHT + 10 or self.rect.left < -20 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-20, 0)
            self.x_velocity = range_with_no_number(-1, 2, 0)

    def shoot(self):
        laser = EnemyLaser(self.rect.centerx, self.rect.bottom)
        all_sprites.add(laser)
        enemy_lasers.add(laser)

# Laser class


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = self.image.get_rect()
        self.rect.centerx = x

    def update(self):
        raise NotImplementedError("Must override method")

# Laser child class


class EnemyLaser(Laser):
    def __init__(self, x, y):
        self.image = enemy_laser_img
        super().__init__(x, y)
        self.rect.top = y
        self.y_velocity = 5

    def update(self):
        self.rect.y += self.y_velocity
        if self.rect.top > HEIGHT:
            self.kill()

# Laser child class


class PlayerLaser(Laser):
    def __init__(self, x, y):
        self.image = player_laser_img
        super().__init__(x, y)
        self.rect.bottom = y
        self.y_velocity = -7

    def update(self):
        self.rect.y += self.y_velocity
        if self.rect.bottom < 0:
            self.kill()


# Load images
background = pygame.image.load(path.join(img_dir, 'spacebg.jpg')).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir, 's1.png')).convert()
regular_enemy_img = pygame.image.load(
    path.join(img_dir, 'enemyShuttle1.png')).convert()
upgraded_enemy_img = pygame.image.load(
    path.join(img_dir, 'enemyShuttle2.png')).convert()
enemy_laser_img = pygame.image.load(path.join(img_dir, 'enemyLaser.png'))
player_laser_img = pygame.image.load(path.join(img_dir, 'playerLaser.png'))

# Load sounds
player_exp_sound = pygame.mixer.Sound(path.join(sound_dir, 'playerExp.wav'))
player_exp_sound.set_volume(0.1)
enemy_exp_sound = pygame.mixer.Sound(path.join(sound_dir, 'enemyExp.flac'))
enemy_exp_sound.set_volume(0.7)
laser_sound = pygame.mixer.Sound(path.join(sound_dir, 'laser.wav'))
laser_sound.set_volume(0.1)
background_sound = pygame.mixer.music.load(path.join(sound_dir, 'theme.ogg'))
pygame.mixer.music.set_volume(0.4)

# Ground different sprites together
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_lasers = pygame.sprite.Group()
enemy_lasers = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# Spawn 7 enemies initially, 2 of them have to me upgraded enemies
for i in range(4):
    e = RegularEnemy()
    all_sprites.add(e)
    enemies.add(e)
for i in range(2):
    e = UpdgradedEnemy()
    all_sprites.add(e)
    enemies.add(e)


pygame.mixer.music.play(loops=-1)
# Custom event to keep track of enemy shots
ENEMYSHOT = pygame.USEREVENT+1
pygame.time.set_timer(ENEMYSHOT, 500)
running = True
# Loop
score = 0
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

        elif event.type == ENEMYSHOT:
            for enemy in enemies:
                if type(enemy) == UpdgradedEnemy:
                    if random.uniform(0, 1) < 0.4:
                        enemy.shoot()

    # Update sprites
    all_sprites.update()

    # Check if the player is hit by an enemy laser
    hits = pygame.sprite.spritecollide(
        player, enemy_lasers, True, pygame.sprite.collide_circle)
    for hit in hits:
        player_exp_sound.play()
        player.health -= 20
        if player.health <= 0:
            running = False

    hits = pygame.sprite.groupcollide(enemies, player_lasers, True, True)

    # Check if an enemy is hit by a players laser
    for hit in hits:
        enemy_exp_sound.play()
        if type(hit) == RegularEnemy:
            score += 10
        else:
            score += 20
        spawn_random_enemy()

    # check if an enemy hit the player
    hits = pygame.sprite.spritecollide(
        player, enemies, True, pygame.sprite.collide_circle)
    for hit in hits:
        player_exp_sound.play()
        player.health -= 40
        if player.health <= 0:
            running = False
        spawn_random_enemy()

    # Render
    window.fill(BLACK)
    window.blit(background, background_rect)
    all_sprites.draw(window)
    draw_text(window, str(score), 22, WIDTH / 2, 10)
    draw_health_bar(window, WIDTH-205, 5, player.health)
    pygame.display.flip()

pygame.quit()
