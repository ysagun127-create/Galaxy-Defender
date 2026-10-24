
import pygame
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import os
import math

# ==========================================
# GALAXY DEFENDER - MCA MINI PROJECT
# ==========================================

pygame.init()

WIDTH = 900
HEIGHT = 650

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Defender")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 17)
big_font = pygame.font.SysFont("arial", 48)

# Colours
WHITE = (255, 255, 255)
BLACK = (5, 8, 25)
BLUE = (60, 180, 255)
RED = (255, 70, 90)
GREEN = (70, 255, 150)
YELLOW = (255, 220, 50)
PURPLE = (180, 90, 255)

# Game states
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

state = MENU

# ==========================================
# NUMPY: PLAYER POSITION AND MOVEMENT
# ==========================================

player_pos = np.array([WIDTH // 2, HEIGHT - 80], dtype=float)

player_speed = 5
player_radius = 22

# ==========================================
# GAME VARIABLES
# ==========================================

score = 0
lives = 3
level = 1

bullets = []
enemies = []
asteroids = []
powerups = []

enemy_spawn_timer = 0
asteroid_spawn_timer = 0

shoot_cooldown = 0
invincible_timer = 0

powerup_active = 0

# Player name
player_name = "Player"

# ==========================================
# BACKGROUND STARS
# ==========================================

stars = []

for i in range(100):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 4)
    ])


def draw_background():
    screen.fill(BLACK)

    for star in stars:
        pygame.draw.circle(
            screen,
            WHITE,
            (star[0], star[1]),
            star[2] // 2 + 1
        )

        star[1] += star[2]

        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)


# ==========================================
# PLAYER
# ==========================================

def draw_player():
    x = int(player_pos[0])
    y = int(player_pos[1])

    # Spaceship body
    points = [
        (x, y - 28),
        (x - 23, y + 22),
        (x, y + 12),
        (x + 23, y + 22)
    ]

    pygame.draw.polygon(screen, BLUE, points)
    pygame.draw.polygon(screen, WHITE, points, 2)

    # Engine flame
    pygame.draw.polygon(
        screen,
        YELLOW,
        [(x - 8, y + 17), (x, y + 35), (x + 8, y + 17)]
    )


def move_player(keys):
    # NumPy direction vector
    direction = np.array([0.0, 0.0])

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        direction[0] -= 1

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        direction[0] += 1

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        direction[1] -= 1

    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        direction[1] += 1

    # Normalize diagonal movement
    length = np.linalg.norm(direction)

    if length > 0:
        direction = direction / length

    player_pos[:] += direction * player_speed

    # Keep spaceship inside window
    player_pos[0] = np.clip(
        player_pos[0], player_radius, WIDTH - player_radius
    )

    player_pos[1] = np.clip(
        player_pos[1], player_radius, HEIGHT - player_radius
    )


# ==========================================
# BULLETS
# ==========================================

def shoot():
    bullet = pygame.Rect(
        int(player_pos[0] - 4),
        int(player_pos[1] - 30),
        8,
        18
    )

    bullets.append(bullet)


def update_bullets():
    for bullet in bullets[:]:
        bullet.y -= 9

        if bullet.bottom < 0:
            bullets.remove(bullet)


def draw_bullets():
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, bullet)


# ==========================================
# ENEMIES
# ==========================================

def spawn_enemy():
    x = random.randint(35, WIDTH - 35)

    enemy = {
        "rect": pygame.Rect(x, -40, 38, 35),
        "speed": random.randint(2, 4) + level,
        "health": 1
    }

    enemies.append(enemy)


def update_enemies():
    for enemy in enemies[:]:
        enemy["rect"].y += enemy["speed"]

        # Enemy reaches bottom
        if enemy["rect"].top > HEIGHT:
            enemies.remove(enemy)


def draw_enemies():
    for enemy in enemies:
        rect = enemy["rect"]

        # Alien body
        pygame.draw.ellipse(screen, RED, rect)

        pygame.draw.circle(
            screen, WHITE,
            (rect.x + 11, rect.y + 12), 5
        )

        pygame.draw.circle(
            screen, WHITE,
            (rect.x + 27, rect.y + 12), 5
        )


# ==========================================
# ASTEROIDS
# ==========================================

def spawn_asteroid():
    x = random.randint(30, WIDTH - 30)

    asteroid = {
        "rect": pygame.Rect(x, -50, 45, 45),
        "speed": random.randint(3, 5)
    }

    asteroids.append(asteroid)


def update_asteroids():
    for asteroid in asteroids[:]:
        asteroid["rect"].y += asteroid["speed"]

        if asteroid["rect"].top > HEIGHT:
            asteroids.remove(asteroid)


def draw_asteroids():
    for asteroid in asteroids:
        rect = asteroid["rect"]

        pygame.draw.circle(
            screen,
            PURPLE,
            rect.center,
            rect.width // 2
        )


# ==========================================
# POWER-UP
# ==========================================

def spawn_powerup(x, y):
    powerups.append(
        pygame.Rect(x, y, 24, 24)
    )


def update_powerups():
    for powerup in powerups[:]:
        powerup.y += 3

        if powerup.top > HEIGHT:
            powerups.remove(powerup)


def draw_powerups():
    for powerup in powerups:
        pygame.draw.circle(
            screen,
            GREEN,
            powerup.center,
            12
        )

        pygame.draw.circle(
            screen,
            WHITE,
            powerup.center,
            12,
            2
        )


# ==========================================
# COLLISION DETECTION
# ==========================================

def check_collisions():
    global score, lives, powerup_active
    global invincible_timer, state

    player_rect = pygame.Rect(
        int(player_pos[0] - player_radius),
        int(player_pos[1] - player_radius),
        player_radius * 2,
        player_radius * 2
    )

    # Bullet hits enemy
    for bullet in bullets[:]:
        for enemy in enemies[:]:

            if bullet.colliderect(enemy["rect"]):

                if bullet in bullets:
                    bullets.remove(bullet)

                if enemy in enemies:
                    enemies.remove(enemy)

                score += 10

                # Chance of a power-up
                if random.random() < 0.15:
                    spawn_powerup(
                        enemy["rect"].x,
                        enemy["rect"].y
                    )

                break

    # Player collects power-up
    for powerup in powerups[:]:
        if player_rect.colliderect(powerup):
            powerups.remove(powerup)

            lives = min(lives + 1, 5)
            powerup_active = 300

    # Player hits enemy or asteroid
    if invincible_timer <= 0:

        for enemy in enemies[:]:
            if player_rect.colliderect(enemy["rect"]):
                enemies.remove(enemy)
                lives -= 1
                invincible_timer = 90
                break

        for asteroid in asteroids[:]:
            if player_rect.colliderect(asteroid["rect"]):
                asteroids.remove(asteroid)
                lives -= 1
                invincible_timer = 90
                break

    if lives <= 0:
        state = GAME_OVER


# ==========================================
# HUD: GAME INFORMATION
# ==========================================

def draw_hud():
    text = font.render(
        f"Score: {score}     Lives: {lives}     Level: {level}",
        True,
        WHITE
    )

    screen.blit(text, (20, 15))

    help_text = small_font.render(
        "Move: Arrow keys/WASD   Shoot: SPACE   Pause: P",
        True,
        WHITE
    )

    screen.blit(help_text, (20, HEIGHT - 28))


# ==========================================
# SAVE PLAYER SCORE USING PANDAS
# ==========================================

def save_score():
    file_name = "galaxy_scores.csv"

    new_record = pd.DataFrame({
        "Player": [player_name],
        "Score": [score],
        "Level": [level]
    })

    if os.path.exists(file_name):
        old_records = pd.read_csv(file_name)

        records = pd.concat(
            [old_records, new_record],
            ignore_index=True
        )
    else:
        records = new_record

    records = records.sort_values(
        by="Score",
        ascending=False
    )

    records.to_csv(file_name, index=False)

    print("\n--- TOP 5 PLAYERS ---")
    print(records.head(5).to_string(index=False))


# ==========================================
# MATPLOTLIB PERFORMANCE DASHBOARD
# ==========================================

def show_analytics():
    file_name = "galaxy_scores.csv"

    if not os.path.exists(file_name):
        print("No score data available yet.")
        return

    data = pd.read_csv(file_name)

    if data.empty:
        print("No score data available.")
        return

    # NumPy calculations
    scores = data["Score"].to_numpy()

    average_score = np.mean(scores)
    highest_score = np.max(scores)

    print("\nAverage score:", average_score)
    print("Highest score:", highest_score)

    # Create charts
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # Score chart
    axes[0].bar(
        data["Player"].head(10),
        data["Score"].head(10)
    )

    axes[0].set_title("Top Player Scores")
    axes[0].set_xlabel("Player")
    axes[0].set_ylabel("Score")

    axes[0].tick_params(axis="x", rotation=45)

    # Score distribution
    axes[1].hist(scores, bins=5)

    axes[1].set_title("Score Distribution")
    axes[1].set_xlabel("Score")
    axes[1].set_ylabel("Number of Games")

    plt.tight_layout()
    plt.show()


# ==========================================
# START MENU
# ==========================================

def draw_menu():
    draw_background()

    title = big_font.render(
        "GALAXY DEFENDER",
        True,
        BLUE
    )

    screen.blit(
        title,
        (WIDTH // 2 - title.get_width() // 2, 180)
    )

    message = font.render(
        "Press ENTER to start your mission",
        True,
        WHITE
    )

    screen.blit(
        message,
        (WIDTH // 2 - message.get_width() // 2, 290)
    )

    instructions = small_font.render(
        "SPACE: Shoot | Arrow keys: Move | A: Analytics | ESC: Quit",
        True,
        GREEN
    )

    screen.blit(
        instructions,
        (WIDTH // 2 - instructions.get_width() // 2, 360)
    )


# ==========================================
# RESET GAME
# ==========================================

def reset_game():
    global player_pos, score, lives, level
    global bullets, enemies, asteroids, powerups
    global enemy_spawn_timer, asteroid_spawn_timer
    global shoot_cooldown, invincible_timer, powerup_active
    global state

    player_pos = np.array(
        [WIDTH // 2, HEIGHT - 80],
        dtype=float
    )

    score = 0
    lives = 3
    level = 1

    bullets = []
    enemies = []
    asteroids = []
    powerups = []

    enemy_spawn_timer = 0
    asteroid_spawn_timer = 0

    shoot_cooldown = 0
    invincible_timer = 0
    powerup_active = 0

    state = PLAYING


# ==========================================
# MAIN GAME LOOP
# ==========================================

def main():
    global state, enemy_spawn_timer
    global asteroid_spawn_timer, shoot_cooldown
    global invincible_timer, powerup_active, level

    running = True
    saved = False

    while running:

        clock.tick(60)

        # Event handling
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if state == MENU:

                    if event.key == pygame.K_RETURN:
                        reset_game()
                        saved = False

                    elif event.key == pygame.K_a:
                        show_analytics()

                    elif event.key == pygame.K_ESCAPE:
                        running = False

                elif state == PLAYING:

                    if event.key == pygame.K_p:
                        state = PAUSED

                    elif event.key == pygame.K_SPACE:
                        if shoot_cooldown <= 0:
                            shoot()
                            shoot_cooldown = 15

                elif state == PAUSED:

                    if event.key == pygame.K_p:
                        state = PLAYING

                    elif event.key == pygame.K_ESCAPE:
                        state = MENU

                elif state == GAME_OVER:

                    if event.key == pygame.K_r:
                        reset_game()
                        saved = False

                    elif event.key == pygame.K_a:
                        show_analytics()

                    elif event.key == pygame.K_ESCAPE:
                        state = MENU

        # ---------------- MENU ----------------

        if state == MENU:
            draw_menu()

        # ---------------- PLAYING ----------------

        elif state == PLAYING:

            draw_background()

            keys = pygame.key.get_pressed()

            move_player(keys)

            # Continuous shooting
            if keys[pygame.K_SPACE] and shoot_cooldown <= 0:
                shoot()
                shoot_cooldown = 15

            if shoot_cooldown > 0:
                shoot_cooldown -= 1

            # Spawn enemies
            enemy_spawn_timer += 1

            if enemy_spawn_timer > max(20, 60 - level * 5):
                spawn_enemy()
                enemy_spawn_timer = 0

            # Spawn asteroids
            asteroid_spawn_timer += 1

            if asteroid_spawn_timer > 100:
                spawn_asteroid()
                asteroid_spawn_timer = 0

            # Update objects
            update_bullets()
            update_enemies()
            update_asteroids()
            update_powerups()

            check_collisions()

            # Increase difficulty
            if score >= level * 100:
                level += 1

            # Timers
            if invincible_timer > 0:
                invincible_timer -= 1

            if powerup_active > 0:
                powerup_active -= 1

            # Draw objects
            draw_bullets()
            draw_enemies()
            draw_asteroids()
            draw_powerups()

            # Flash player after taking damage
            if invincible_timer == 0 or invincible_timer % 10 < 5:
                draw_player()

            draw_hud()

        # ---------------- PAUSED ----------------

        elif state == PAUSED:

            draw_background()

            pause_text = big_font.render(
                "PAUSED",
                True,
                YELLOW
            )

            screen.blit(
                pause_text,
                (WIDTH // 2 - pause_text.get_width() // 2, 260)
            )

            hint = font.render(
                "Press P to continue",
                True,
                WHITE
            )

            screen.blit(
                hint,
                (WIDTH // 2 - hint.get_width() // 2, 330)
            )

        # ---------------- GAME OVER ----------------

        elif state == GAME_OVER:

            draw_background()

            if not saved:
                save_score()
                saved = True

            title = big_font.render(
                "MISSION FAILED",
                True,
                RED
            )

            screen.blit(
                title,
                (WIDTH // 2 - title.get_width() // 2, 180)
            )

            result = font.render(
                f"Final Score: {score}    Level: {level}",
                True,
                WHITE
            )

            screen.blit(
                result,
                (WIDTH // 2 - result.get_width() // 2, 270)
            )

            instructions = small_font.render(
                "R: Play Again    A: View Analytics    ESC: Main Menu",
                True,
                GREEN
            )

            screen.blit(
                instructions,
                (WIDTH // 2 - instructions.get_width() // 2, 350)
            )

        pygame.display.flip()

    pygame.quit()


# ==========================================
# RUN THE GAME
# ==========================================

if __name__ == "__main__":

    player_name = input("Enter your player name: ").strip()

    if not player_name:
        player_name = "Player"

    main()
