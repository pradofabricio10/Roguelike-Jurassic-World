# coding=utf-8
import random
import math
import sys
import time 
from pgzero.rect import Rect

# Game settings
WIDTH = 800
HEIGHT = 600
TITLE = "Roguelike de Aventura Jurassic World"
FPS = 60

# RGB colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
DARK_GRAY = (40, 40, 40)

# Sound and music mapping
music_on = True
background_music = 'space_music'
explosion_sound = 'explosion'
shoot_sound = 'laser'

# Game states
MENU = 0
GAME_RUNNING = 1
GAME_OVER = 2
GAME_WIN = 3
current_state = MENU

# Game variables and map
TILE_SIZE = 64
PLAYER_SPEED = 2
ENEMY_SPEED = 0.4
PROJECTILE_SPEED = 5

level_map = [
    "################",
    "#..............#",
    "#..####........#",
    "#..#..#........#",
    "#..#..#........#",
    "#..#..#........#",
    "#..####........#",
    "#..............#",
    "################",
]

player = None
enemies = []
projectiles = []

collision_timer = 0.0

try:
    background_image = images.cenario
except Exception as e:
    print(f"ERRO: Nao foi possivel carregar a imagem de fundo 'cenario'. Verifique se o arquivo esta na pasta 'images/'.")
    sys.exit()

class Projectile:
    """
    Representa o projetil atirado pelo jogador.
    """
    def __init__(self, pos, direction):
        self.actor = Actor('bola', pos=pos)
        self.actor.scale = 0.05
        self.direction = direction
        self.speed = PROJECTILE_SPEED

    def update(self):
        self.actor.x += self.direction[0] * self.speed
        self.actor.y += self.direction[1] * self.speed

    def draw(self):
        self.actor.draw()

class AnimatedSprite:
    """
    Base class for managing animated sprites.
    """
    def __init__(self, sprite_name, num_frames, frame_rate=10, initial_pos=(0, 0)):
        self.frames = [f'{sprite_name}{i}' for i in range(1, num_frames + 1)]
        self.current_frame = 0
        self.frame_rate = frame_rate
        self.frame_timer = 0
        try:
            self.actor = Actor(self.frames[0], pos=initial_pos)
            self.actor.scale = 0.05
            print(f"SUCESSO: O sprite '{self.frames[0]}' foi carregado.")
        except Exception as e:
            print(f"ERRO: Nao foi possivel carregar o sprite '{self.frames[0]}'.")
            print("Verifique se o arquivo esta na pasta 'images/' e se o nome do arquivo nao tem a extensao '.jpg' ou '.png' no codigo.")
            print(f"Detalhes do erro: {e}")
            sys.exit()

    def update_animation(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= 1.0 / self.frame_rate:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.actor.image = self.frames[self.current_frame]

    def draw(self):
        self.actor.draw()

class Player(AnimatedSprite):
    """
    Represents the player.
    """
    def __init__(self, pos):
        super().__init__('player_walk', 4, frame_rate=8, initial_pos=pos)
        self.speed = PLAYER_SPEED
        self.is_moving = False
        self.last_shot_time = 0.0
        self.last_direction = (0, -1)

    def update(self, dt):
        self.is_moving = False
        dx, dy = 0, 0

        if keyboard.up:
            dy = -1
            self.is_moving = True
        if keyboard.down:
            dy = 1
            self.is_moving = True
        if keyboard.left:
            dx = -1
            self.is_moving = True
        if keyboard.right:
            dx = 1
            self.is_moving = True

        if dx != 0 or dy != 0:
            self.last_direction = (dx, dy) 
            dist = math.sqrt(dx**2 + dy**2)
            self.actor.x += (dx / dist) * self.speed
            self.actor.y += (dy / dist) * self.speed
        
        if self.is_moving:
            self.update_animation(dt)
        else:
            self.actor.image = self.frames[0]

    def shoot(self, current_time):
        global projectiles
        if current_time - self.last_shot_time > 0.5:
            direction = self.last_direction 
            
            dist = math.sqrt(direction[0]**2 + direction[1]**2)
            if dist > 0:
                direction = (direction[0] / dist, direction[1] / dist)
            
            projectiles.append(Projectile(self.actor.pos, direction))
            self.last_shot_time = current_time
            try:
                sounds.shoot.play()
            except Exception as e:
                print(f"ERRO: Nao foi possivel tocar o som '{shoot_sound}'.")

class Enemy(AnimatedSprite):
    """
    Represents an enemy.
    """
    def __init__(self, pos):
        super().__init__('enemy_idle', 4, frame_rate=5, initial_pos=pos)
        self.speed = ENEMY_SPEED

    def update(self, dt, player_pos):
        dx = player_pos[0] - self.actor.x
        dy = player_pos[1] - self.actor.y
        dist = math.sqrt(dx**2 + dy**2)
        
        if dist > 0:
            self.actor.x += (dx / dist) * self.speed
            self.actor.y += (dy / dist) * self.speed
        
        self.update_animation(dt)

def draw_menu():
    """
    Draws the main menu on the screen.
    """
    screen.fill(BLACK)
    screen.draw.text("Jurassic World", center=(WIDTH // 2, HEIGHT // 4), color=WHITE, fontsize=72)
    
    start_button = Rect(WIDTH // 2 - 120, HEIGHT // 2, 240, 50)
    music_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 70, 240, 50)
    exit_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 140, 240, 50)

    screen.draw.filled_rect(start_button, GRAY)
    screen.draw.filled_rect(music_button, GRAY)
    screen.draw.filled_rect(exit_button, GRAY)

    screen.draw.text("Comecar o Jogo", center=start_button.center, color=WHITE, fontsize=36)
    screen.draw.text(f"Musica: {'ON' if music_on else 'OFF'}", center=music_button.center, color=WHITE, fontsize=36)
    screen.draw.text("Sair", center=exit_button.center, color=WHITE, fontsize=36)

def draw_win_screen():
    """
    Desenha a tela de vitoria.
    """
    screen.fill(GREEN)
    screen.draw.text("VOCE VENCEU!", center=(WIDTH // 2, HEIGHT // 2 - 50), color=WHITE, fontsize=100)
    
    restart_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 70, 240, 50)
    exit_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 140, 240, 50)
    
    screen.draw.filled_rect(restart_button, GRAY)
    screen.draw.filled_rect(exit_button, GRAY)
    
    screen.draw.text("Reiniciar", center=restart_button.center, color=WHITE, fontsize=36)
    screen.draw.text("Sair", center=exit_button.center, color=WHITE, fontsize=36)

def draw_instructions():
    """
    Desenha uma caixa com as instrucoes de controle na parte superior da tela.
    """
    box = Rect(0, 0, WIDTH, 45)
    screen.draw.filled_rect(box, DARK_GRAY)
    screen.draw.rect(box, WHITE)
    
    instructions_text = "Controles: Setas para Mover | Espaco para Atirar"
    screen.draw.text(instructions_text, center=(WIDTH // 2, 22), color=WHITE, fontsize=24)

def handle_menu_click(pos):
    """
    Handles mouse clicks in the menu.
    """
    global current_state, music_on
    start_button = Rect(WIDTH // 2 - 120, HEIGHT // 2, 240, 50)
    music_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 70, 240, 50)
    exit_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 140, 240, 50)

    if start_button.collidepoint(pos):
        current_state = GAME_RUNNING
        init_game()
        play_music()
    elif music_button.collidepoint(pos):
        music_on = not music_on
        if music_on:
            play_music()
        else:
            music.stop()
    elif exit_button.collidepoint(pos):
        sys.exit()

def handle_game_over_click(pos):
    """
    Handles mouse clicks on the game over screen.
    """
    global current_state
    restart_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 70, 240, 50)
    exit_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 140, 240, 50)

    if restart_button.collidepoint(pos):
        current_state = GAME_RUNNING
        init_game()
        play_music()
    elif exit_button.collidepoint(pos):
        sys.exit()

def handle_win_click(pos):
    """
    Lida com cliques na tela de vitoria.
    """
    global current_state
    restart_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 70, 240, 50)
    exit_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 140, 240, 50)
    
    if restart_button.collidepoint(pos):
        current_state = GAME_RUNNING
        init_game()
        play_music()
    elif exit_button.collidepoint(pos):
        sys.exit()

def play_music():
    """
    Plays the background music if the option is enabled.
    """
    if music_on:
        try:
            music.play(background_music)
            music.set_volume(0.5)
        except Exception as e:
            print(f"ERRO: Nao foi possivel tocar a musica '{background_music}'. Verifique se o arquivo '{background_music}.mp3' (ou .ogg, .wav) esta na pasta 'music/'.")
            print(f"Detalhes do erro: {e}")

def init_game():
    """
    Initializes game variables and objects.
    """
    global player, enemies, projectiles, collision_timer
    player_pos = (WIDTH // 2, HEIGHT // 2)
    player = Player(player_pos)

    enemies = []
    while True:
        pos_x = random.randint(100, WIDTH - 100)
        pos_y = random.randint(100, HEIGHT - 100)
        
        distance = math.sqrt((pos_x - player_pos[0])**2 + (pos_y - player_pos[1])**2)
        
        if distance > 300: 
            break
            
    enemies.append(Enemy((pos_x, pos_y)))
    
    projectiles = []
    collision_timer = 0.0
    
    print("Jogo inicializado. Verifique o terminal para mensagens de erro caso os personagens nao aparecam.")

def on_mouse_down(pos):
    """
    Called when a mouse button is pressed.
    """
    if current_state == MENU:
        handle_menu_click(pos)
    elif current_state == GAME_OVER:
        handle_game_over_click(pos)
    elif current_state == GAME_WIN:
        handle_win_click(pos)

def on_key_down(key):
    global current_state, player
    if current_state == GAME_RUNNING and key == keys.SPACE and player:
        player.shoot(time.time())

def update(dt):
    """
    Updates the game state. Called every frame.
    """
    global current_state, collision_timer, enemies, projectiles
    if current_state == GAME_RUNNING:
        collision_timer += dt
        
        if player is not None:
            player.update(dt)
            
            projectiles_to_remove = []
            enemies_to_remove = []
            
            for p in projectiles:
                p.update()
                if p.actor.x < 0 or p.actor.x > WIDTH or p.actor.y < 0 or p.actor.y > HEIGHT:
                    projectiles_to_remove.append(p)
                
                for enemy in enemies:
                    if p.actor.colliderect(enemy.actor):
                        projectiles_to_remove.append(p)
                        enemies_to_remove.append(enemy)
                        try:
                            sounds.explosion.play()
                        except Exception as e:
                            print(f"ERRO: Nao foi possivel tocar o som '{explosion_sound}'.")

            projectiles = [p for p in projectiles if p not in projectiles_to_remove]
            enemies = [e for e in enemies if e not in enemies_to_remove]
            
            if not enemies:
                current_state = GAME_WIN
                music.stop()

            for enemy in enemies:
                enemy.update(dt, player.actor.pos)
                
                if collision_timer > 0.5:
                    if player.actor.colliderect(enemy.actor):
                        current_state = GAME_OVER
                        music.stop()
                        try:
                            sounds.explosion.play()
                        except Exception as e:
                            print(f"ERRO: Nao foi possivel tocar o som '{explosion_sound}'.")

def draw():
    """
    Draws the game screen. Called every frame.
    """
    if current_state == MENU:
        draw_menu()
    elif current_state == GAME_RUNNING:
        screen.blit(background_image, (0, 0))
        if player is not None:
            player.draw()
            for enemy in enemies:
                enemy.draw()
            for p in projectiles:
                p.draw()
            draw_instructions()
    elif current_state == GAME_OVER:
        screen.fill(BLACK)
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 50), color=RED, fontsize=100)
        
        restart_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 70, 240, 50)
        exit_button = Rect(WIDTH // 2 - 120, HEIGHT // 2 + 140, 240, 50)
        
        screen.draw.filled_rect(restart_button, GRAY)
        screen.draw.filled_rect(exit_button, GRAY)
        
        screen.draw.text("Reiniciar", center=restart_button.center, color=WHITE, fontsize=36)
        screen.draw.text("Sair", center=exit_button.center, color=WHITE, fontsize=36)
    elif current_state == GAME_WIN:
        draw_win_screen()