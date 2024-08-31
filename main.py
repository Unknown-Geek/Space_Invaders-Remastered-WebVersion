import random
import math
import pygame
from pygame import mixer
import cv2
from cvzone.HandTrackingModule import HandDetector
import sqlite3
from datetime import datetime

# Database setup
def setup_database():
    conn = sqlite3.connect('space_invaders.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        timestamp TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Insert score into database
def insert_score(player_name, score):
    conn = sqlite3.connect('space_invaders.db')
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('''
    INSERT INTO users_scores (player_name, score, timestamp)
    VALUES (?, ?, ?)
    ''', (player_name, score, timestamp))
    conn.commit()
    conn.close()

def get_top_scores(limit=10):
    conn = sqlite3.connect('space_invaders.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT player_name, score, timestamp
    FROM users_scores
    ORDER BY score DESC
    LIMIT ?
    ''', (limit,))
    top_scores = cursor.fetchall()
    conn.close()
    return top_scores

def get_latest_scores(limit=10):
    conn = sqlite3.connect('space_invaders.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT player_name, score, timestamp
    FROM users_scores
    ORDER BY timestamp DESC
    LIMIT ?
    ''', (limit,))
    latest_scores = cursor.fetchall()
    conn.close()
    return latest_scores

def display_top_scores(screen, font):
    top_scores = get_top_scores(5)  # Get top 5 scores
    y_offset = 100
    for score in top_scores:
        score_text = font.render(f"{score[0]}: {score[1]}", True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, y_offset))
        y_offset += 40

def display_scores_page(screen, clock):
    running = True
    font = pygame.font.Font('freesansbold.ttf', 24)
    title_font = pygame.font.Font('freesansbold.ttf', 32)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        update_background()
        draw_background(screen)

        # Title
        title = title_font.render('SCORES', True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        # Latest 10 scores
        latest_scores = get_latest_scores(10)
        y_offset = 100
        screen.blit(font.render("Latest Scores:", True, (255, 255, 255)), (50, y_offset))
        y_offset += 30
        for score in latest_scores:
            score_text = font.render(f"{score[0]}: {score[1]} - {score[2][:16]}", True, (255, 255, 255))
            screen.blit(score_text, (50, y_offset))
            y_offset += 30

        # Top 3 leaderboard
        top_scores = get_top_scores(3)
        y_offset = 100
        screen.blit(font.render("Leaderboard:", True, (255, 255, 255)), (SCREEN_WIDTH - 300, y_offset))
        y_offset += 30
        for i, score in enumerate(top_scores):
            score_text = font.render(f"{i+1}. {score[0]}: {score[1]}", True, (255, 255, 255))
            screen.blit(score_text, (SCREEN_WIDTH - 300, y_offset))
            y_offset += 30

        # Instructions
        instructions = font.render("Press ESC to return to main menu", True, (255, 255, 255))
        screen.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, SCREEN_HEIGHT - 50))

        pygame.display.flip()
        clock.tick(30)

#Instructions Page
def display_instructions_page(screen, clock):
    running = True
    font = pygame.font.Font('freesansbold.ttf', 24)
    title_font = pygame.font.Font('freesansbold.ttf', 32)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        update_background()
        draw_background(screen)

        # Title
        title = title_font.render('INSTRUCTIONS', True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        # Instructions
        instructions = [
            "1. Right Hand - Tilt left or right to move the player.",
            "2. Left Hand - Show all fingers to shoot bullets.",
            "3. Avoid enemy spaceships. Shoot them to earn points.",
            "4. The game gets harder over time. Good luck!",
            "5. Press ESC to return to the main menu."
        ]
        y_offset = 125
        for instruction in instructions:
            instruction_text = font.render(instruction, True, (255, 255, 255))
            screen.blit(instruction_text, (80, y_offset))
            y_offset += 50

        pygame.display.flip()
        clock.tick(30)

def start_screen(screen, clock):
    setup_database()  # Set up the SQLite database
    input_active = True
    user_text = ''
    input_box = pygame.Rect(SCREEN_WIDTH//2 - 100, 300, 200, 50)
    color = pygame.Color('lightskyblue3')
    font = pygame.font.Font(None, 32)
    title_font = pygame.font.Font('freesansbold.ttf', 64)
    
    # Create a button for the Scores page
    scores_button = pygame.Rect(SCREEN_WIDTH//2 - 50, 375, 100, 50)
    button_color = pygame.Color('dodgerblue2')

    # Create a button for the Instructions page
    instructions_button = pygame.Rect(SCREEN_WIDTH//2 - 80, 450, 160, 50)
    button_color = pygame.Color('dodgerblue2')
    
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return False
                elif event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if scores_button.collidepoint(event.pos):
                    display_scores_page(screen, clock)
                if instructions_button.collidepoint(event.pos):
                    display_instructions_page(screen, clock)
        
        update_background()
        draw_background(screen)
        
        title = title_font.render('SPACE INVADERS', True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        # Render the current text.
        txt_surface = font.render(user_text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        
        prompt_text = font.render('Enter your name and press Enter:', True, (255, 255, 255))
        screen.blit(prompt_text, (SCREEN_WIDTH//2 - prompt_text.get_width()//2, 250))
        
        # Draw the Scores button
        pygame.draw.rect(screen, button_color, scores_button)
        scores_text = font.render('Scores', True, (255, 255, 255))
        screen.blit(scores_text, (scores_button.x + (scores_button.width - scores_text.get_width()) // 2,
                                  scores_button.y + (scores_button.height - scores_text.get_height()) // 2))
        
        # Draw the Instructions button
        pygame.draw.rect(screen, button_color, instructions_button)
        instructions_text = font.render('Instructions', True, (255, 255, 255))
        screen.blit(instructions_text, (instructions_button.x + (instructions_button.width - scores_text.get_width()) // 2 - 28,
                                  instructions_button.y + (instructions_button.height - scores_text.get_height()) // 2))
        
        pygame.display.flip()
        clock.tick(30)
    
    return user_text

# AI setup
detector = HandDetector(detectionCon=0.8, maxHands=2)
cap = cv2.VideoCapture(0)
tilt_threshold = 20

# Game setup
pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Scrolling Background
background_img = pygame.image.load('background.jpg')
background_height = background_img.get_rect().height
background_rect1 = background_img.get_rect()
background_rect2 = background_img.get_rect()
background_rect1.bottom = SCREEN_HEIGHT
background_rect2.bottom = background_rect1.top
background_speed = 1

def update_background():
    global background_rect1, background_rect2
    background_rect1.y += background_speed
    background_rect2.y += background_speed

    if background_rect1.top >= SCREEN_HEIGHT:
        background_rect1.bottom = background_rect2.top
    if background_rect2.top >= SCREEN_HEIGHT:
        background_rect2.bottom = background_rect1.top

def draw_background(surface):
    surface.blit(background_img, background_rect1)
    surface.blit(background_img, background_rect2)

# Title and icon
pygame.display.set_caption('Space Invaders')
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# BGM
mixer.music.load('background.wav')
mixer.music.play(-1)

# Player
playerImg = pygame.image.load('arcade-game.png')
playerX = 400
playerY = 450
player_velocity = 0
player_acceleration = 0.5
player_lerp_factor = 0.1

# Bullet
bulletImg = pygame.image.load('bullet (1).png')
bullets = []
bullet_cooldown = 0.5
last_bullet_time = 0
bulletY_change = 15

# Enemy
no_enemies = 5
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
enemy_direction = []  # Track the vertical direction of each enemy
enemy_speed = 2.5

for i in range(no_enemies):
    enemyImg.append(pygame.image.load('icons8-spaceship-64.png'))
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(50, 150))  # Limit initial vertical position
    enemyX_change.append(2)
    enemyY_change.append(1)
    enemy_direction.append(1)  # Start moving downwards

# Score
score = 0
font = pygame.font.Font('freesansbold.ttf', 30)
title_font = pygame.font.Font('freesansbold.ttf', 64)

# Difficulty
difficulty_multiplier = 1.0
difficulty_increase_rate = 0.2
last_difficulty_increase = 0

def show_score():
    score_value = font.render('Score : ' + str(score), True, (255, 255, 255))
    screen.blit(score_value, (10, 10))

def game_over(user_text):
    global score, playerX, playerY, bullets, enemyX, enemyY, enemy_direction
    mixer.music.stop()
    mixer.music.load('game_over.mp3')
    mixer.music.set_volume(2.5)
    mixer.music.play(1)
    gameoverImg = pygame.image.load('game over.png')
    
    # Insert score into database
    insert_score(user_text, score)
    
    for i in range(5, 0, -1):
        screen.blit(gameoverImg, (0, 0))
        scoreimg = font.render('YOU SCORED : ' + str(score), True, (255, 255, 255))
        screen.blit(scoreimg, (420, 480))
        exit_time = font.render('Game restarts in  ' + str(i) + ' sec', True, (255, 255, 255))
        screen.blit(exit_time, (420, 520))
        pygame.display.flip()
        pygame.time.delay(1000)
    # Reset game state
    score = 0
    playerX = 400
    playerY = 450
    bullets = []
    for i in range(no_enemies):
        enemyX[i] = random.randint(0, 736)
        enemyY[i] = random.randint(50, 150)
        enemy_direction[i] = 1
    mixer.music.load('background.wav')
    mixer.music.play(-1)

def isCollision(x1, y1, x2, y2):
    distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return distance < 30

running = True
game_state = "START"

while running:
    dt = clock.tick(60) / 1000.0  # 60 FPS, convert to seconds

    if game_state == "START":
        user_text = start_screen(screen, clock)
        if user_text:
            game_state = "PLAYING"
        else:
            running = False
            continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update and draw scrolling background
    update_background()
    draw_background(screen)

    # Increase difficulty over time
    current_time = pygame.time.get_ticks() / 1000.0
    if current_time - last_difficulty_increase > 10:  # Increase difficulty every 10 seconds
        difficulty_multiplier += difficulty_increase_rate
        last_difficulty_increase = current_time

    player_velocity = player_velocity * (1 - player_lerp_factor) 
    new_player_x = playerX + player_velocity * dt * 60

    # Boundary check
    if new_player_x < 0:
        new_player_x = 0
        player_velocity = 0
    elif new_player_x > 736:
        new_player_x = 736
        player_velocity = 0

    playerX = new_player_x  # Direct assignment instead of lerping

    # Enemy movement (zigzag pattern)
    for i in range(no_enemies):
        enemy_speed = enemyX_change[i] * difficulty_multiplier
        enemyX[i] += enemy_speed * dt * 60
        
        # Zigzag motion
        if enemyX[i] >= 736:
            enemyX[i] = 736
            enemyX_change[i] *= -1
            enemy_direction[i] *= -1
        
        if enemyX[i] <= 0:
            enemyX[i] = 0
            enemyX_change[i] *= -1
            enemy_direction[i] *= -1

        if enemyY[i] <= 50:
            enemyY[i] = 50
            enemyY_change[i] *= -1
            enemy_direction[i] *= -1

        enemyY[i] += enemy_direction[i] * enemy_speed * dt * 5  # Adjust descent speed as needed

        # Ensure the enemy stays within vertical bounds
        enemyY[i] = max(0, min(450, enemyY[i]))

        # Game over condition
        if enemyY[i] > 430:
            game_over(user_text)
            game_state = "START"
            break

        # Collision detection
        for bullet in bullets[:]:
            if isCollision(enemyX[i], enemyY[i], bullet[0], bullet[1]) or isCollision(playerX, playerY, enemyX[i], enemyY[i]):
                explosion_sound = mixer.Sound('explosion.wav')
                explosion_sound.play()
                bullets.remove(bullet)
                score += 10
                enemyX[i] = random.randint(10, 730)
                enemyY[i] = random.randint(50, 150)

        screen.blit(enemyImg[i], (int(enemyX[i]), int(enemyY[i])))

    # Bullet movement
    for bullet in bullets[:]:
        bullet[1] -= bulletY_change * dt * 60
        if bullet[1] < 0:
            bullets.remove(bullet)
        else:
            screen.blit(bulletImg, (int(bullet[0]), int(bullet[1])))

    # AI hand tracking
    success, img = cap.read()
    hands, img = detector.findHands(img)
    if hands:
        for hand in hands:
            if hand['type'] == 'Right':
                wrist = hand['lmList'][0][:2]
                middle_finger_tip = hand['lmList'][12][:2]
                
                dx = middle_finger_tip[0] - wrist[0]
                dy = middle_finger_tip[1] - wrist[1]
                angle = math.degrees(math.atan2(dy, dx))
                
                if angle > -90 - tilt_threshold:
                    player_velocity -= player_acceleration
                elif angle < -90 + tilt_threshold:
                    player_velocity += player_acceleration
                
                cv2.line(img, tuple(wrist), tuple(middle_finger_tip), (255, 0, 0), 2)
                cv2.putText(img, f"Angle: {angle:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            if hand['type'] == 'Left':
                fingerUp = detector.fingersUp(hand)
                if fingerUp == [1,1,1,1,1]:
                    current_time = pygame.time.get_ticks() / 1000.0
                    if current_time - last_bullet_time > bullet_cooldown:
                        laser_sound = mixer.Sound('laser.wav')
                        laser_sound.play()
                        bullets.append([playerX + 16, playerY - 20])
                        last_bullet_time = current_time 

    small_frame = cv2.resize(img, (0,0), fx=0.3, fy=0.25)
    cv2.imshow('frame', small_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    screen.blit(playerImg, (int(playerX), int(playerY)))
    show_score()
    pygame.display.flip()

cap.release()
cv2.destroyAllWindows()
pygame.quit()