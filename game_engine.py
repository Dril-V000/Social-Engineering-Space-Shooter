import pygame
import random
import os
import sys
import time

def show_loading_screen():
    if not pygame.get_init():
        return
    try:
        WIDTH, HEIGHT = 600, 600
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Loading Game...")
        font = pygame.font.SysFont("Arial", 24)
        loading_texts = [
            "Initializing game engine...",
            "Loading assets...",
            "Checking system requirements...",
            "testing your pc ...",
            "Preparing gameplay...",
            "Almost ready..."
        ]
        for i, text in enumerate(loading_texts):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            screen.fill((30, 30, 50))
            title = font.render("Space Shooter Game", True, (255, 255, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))
            loading = font.render(text, True, (200, 200, 255))
            screen.blit(loading, (WIDTH // 2 - loading.get_width() // 2, 100))
            progress = (i + 1) / len(loading_texts)
            pygame.draw.rect(screen, (50, 50, 80), (50, 140, WIDTH - 100, 20))
            pygame.draw.rect(screen, (70, 130, 180), (50, 140, (WIDTH - 100) * progress, 20))
            pygame.display.flip()
            time.sleep(random.uniform(0.3, 0.8))
        time.sleep(0.5)
    except:
        pass

def get_resource_path():
    try:
        return sys._MEIPASS
    except:
        return os.path.abspath(".")

def load_image(file_name):
    try:
        base_path = get_resource_path()
        full_path = os.path.join(base_path, file_name)
        if not os.path.exists(full_path):
            assets_path = os.path.join(base_path, "assets", os.path.basename(file_name))
            if os.path.exists(assets_path):
                full_path = assets_path
            else:
                raise FileNotFoundError()
        image = pygame.image.load(full_path)
        return image.convert_alpha() if file_name.endswith('.png') else image.convert()
    except:
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(surface, (255, 100, 100), (0, 0, 50, 50), border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), (10, 10, 30, 30), border_radius=5)
        return surface

def load_sound(file_name):
    try:
        base_path = get_resource_path()
        full_path = os.path.join(base_path, file_name)
        if not os.path.exists(full_path):
            assets_path = os.path.join(base_path, "assets", os.path.basename(file_name))
            if os.path.exists(assets_path):
                full_path = assets_path
            else:
                raise FileNotFoundError()
        return pygame.mixer.Sound(full_path)
    except:
        return None

if not pygame.get_init():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=4, buffer=512)

WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Game")

main_font = pygame.font.SysFont("comicsans", 35)
lost_font = pygame.font.SysFont("comicsans", 45)
score_font = pygame.font.SysFont("comicsans", 30)

HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as file:
                content = file.read().strip()
                if content.isdigit():
                    return int(content)
        return 0
    except:
        return 0

def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as file:
            file.write(str(score))
    except:
        pass

def update_high_score(current_score):
    high_score = load_high_score()
    if current_score > high_score:
        save_high_score(current_score)
        return current_score
    return high_score

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

def draw_lives(lives):
    WIN.blit(main_font.render(f"Lives: {lives}", 1, (255, 255, 255)), (10, 10))

def draw_level(level):
    level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
    WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

def draw_score(score, high_score):
    WIN.blit(score_font.render(f"Score: {score}", 1, (255, 255, 255)), (WIDTH // 2 - 50, 10))
    WIN.blit(score_font.render(f"High Score: {high_score}", 1, (255, 215, 0)), (10, 50))

def draw_lost(score, high_score):
    WIN.blit(lost_font.render("Game Over!", 1, (255, 255, 255)), (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    WIN.blit(main_font.render(f"Final Score: {score}", 1, (255, 255, 255)), (WIDTH // 2 - 100, HEIGHT // 2 + 10))
    WIN.blit(main_font.render(f"High Score: {high_score}", 1, (255, 215, 0)), (WIDTH // 2 - 100, HEIGHT // 2 + 50))
    WIN.blit(score_font.render("Press R to restart or ESC to quit", 1, (200, 200, 200)), (WIDTH // 2 - 150, HEIGHT // 2 + 100))

RED_SPACE_SHIP = load_image("pixel_ship_red_small.png")
GREEN_SPACE_SHIP = load_image("pixel_ship_green_small.png")
BLUE_SPACE_SHIP = load_image("pixel_ship_blue_small.png")
YELLOW_SPACE_SHIP = load_image("pixel_ship_yellow.png")

RED_LASER = load_image("pixel_laser_red.png")
GREEN_LASER = load_image("pixel_laser_green.png")
BLUE_LASER = load_image("pixel_laser_blue.png")
YELLOW_LASER = load_image("pixel_laser_yellow.png")

BG = pygame.transform.scale(load_image("background-black.png"), (WIDTH, HEIGHT))

SHOOT_SOUND = load_sound("shoot.mp3")
EXPLOSION_SOUND = load_sound("explosion.mp3")
if SHOOT_SOUND:
    SHOOT_SOUND.set_volume(0.5)
if EXPLOSION_SOUND:
    EXPLOSION_SOUND.set_volume(0.7)

try:
    pygame.mixer.music.load(os.path.join(get_resource_path(), "assets", "music.mp3"))
    pygame.mixer.music.set_volume(0.15)
    pygame.mixer.music.play(-1)
except:
    pass

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
    def move(self, vel):
        self.y += vel
    def off_screen(self, height):
        return self.y > height or self.y < 0
    def collision(self, obj):
        return collide(self, obj)
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

class Ship:
    FRAMES_BETWEEN_SHOTS = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.frames_counter = 0
        self.mask = None
    def move_lasers(self, vel, obj):
        self.frames_counter -= 1
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)
    def shoot(self):
        if self.frames_counter <= 0:
            laser = Laser(self.x + self.get_width() // 2 - 10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.frames_counter = self.FRAMES_BETWEEN_SHOTS
            if SHOOT_SOUND:
                pygame.mixer.Channel(0).play(SHOOT_SOUND)
    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
    def move_lasers(self, vel, objs):
        self.frames_counter -= 1
        hit_enemy = False
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs[:]:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        if EXPLOSION_SOUND:
                            pygame.mixer.Channel(1).play(EXPLOSION_SOUND)
                        hit_enemy = True
                        break
        return hit_enemy
    def draw(self, window):
        super().draw(window)
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {"red": (RED_SPACE_SHIP, RED_LASER), "green": (GREEN_SPACE_SHIP, GREEN_LASER), "blue": (BLUE_SPACE_SHIP, BLUE_LASER)}
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.points = {"red": 100, "green": 150, "blue": 200}[color]
        self.can_shoot = random.random() < 0.4
        self.shoot_timer = 0
        self.shoot_delay = random.randint(60, 180)
    def move(self, vel):
        self.y += vel
        self.shoot_timer += 1

    def shoot(self):
        if (self.y > 0 and 
                self.can_shoot and
                self.shoot_timer >= self.shoot_delay and
                self.frames_counter <= 0):

            laser = Laser(self.x + self.get_width() // 2 - 10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.frames_counter = self.FRAMES_BETWEEN_SHOTS
            self.shoot_timer = 0
            self.shoot_delay = random.randint(60, 180)
            if SHOOT_SOUND:
                pygame.mixer.Channel(3).play(SHOOT_SOUND)

def main():
    run = True
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2, HEIGHT - 100)
    enemies = []
    level = 0
    lives = 5
    score = 0
    high_score = load_high_score()
    enemy_vel = 1
    laser_vel = 5
    enemy_spawn_timer = 0
    wave_length = 5
    player_vel = 5
    shoot_pressed = False
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shoot_pressed = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    shoot_pressed = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:
            player.y += player_vel
        if shoot_pressed:
            player.shoot()
        if keys[pygame.K_ESCAPE]:
            return "quit"
        enemy_spawn_timer += 1
        if enemy_spawn_timer > 120:
            if len(enemies) == 0:
                level += 1
                wave_length += 3
                for i in range(wave_length):
                    color = random.choice(["red", "blue", "green"])
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), color)
                    enemies.append(enemy)
                enemy_spawn_timer = 0
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.shoot()
            enemy.move_lasers(laser_vel, player)
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
                if player.health <= 0:
                    lives -= 1
                    player.health = 100
        hit_enemy = player.move_lasers(-laser_vel, enemies)
        if hit_enemy:
            score += 100
        WIN.blit(BG, (0, 0))
        for enemy in enemies:
            enemy.draw(WIN)
        player.draw(WIN)
        draw_lives(lives)
        draw_level(level)
        draw_score(score, high_score)
        pygame.display.update()
        if lives <= 0 or player.health <= 0:
            high_score = update_high_score(score)
            draw_lost(score, high_score)
            pygame.display.update()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "quit"
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            return "restart"
                        elif event.key == pygame.K_ESCAPE:
                            return "quit"
                clock.tick(60)
    return "quit"

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 45)
    high_score = load_high_score()
    while True:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Space Shooter Game", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH // 2 - title_label.get_width() // 2, 150))
        high_score_label = main_font.render(f"High Score: {high_score}", 1, (255, 215, 0))
        WIN.blit(high_score_label, (WIDTH // 2 - high_score_label.get_width() // 2, 220))
        instructions = score_font.render("Click to begin", 1, (200, 200, 200))
        WIN.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 350))
        controls = score_font.render("Controls: WASD to move, SPACE to shoot", 1, (150, 150, 255))
        WIN.blit(controls, (WIDTH // 2 - controls.get_width() // 2, 450))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "play"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "quit"

def start():
    try:
        while True:
            action = main_menu()
            if action == "play":
                result = main()
                if result == "quit":
                    break
            elif action == "quit":
                break
    finally:
        from main import clean

        clean()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    start()
