from ursina import *
import random
import time
import threading 
from FilteringOnPython import process_imu_data  

app = Ursina()
window.size = (1152, 720)
window.color = color.rgb32(154, 42, 42)


player_name = ""  # Store the player's name
game_started = False  # Flag to track if the game has started

# Startup Screen Elements

game_title = Text(text="Viral Vengeance", position=(0, 0.25), scale=3, color=color.yellow, origin=(0, 0), bold=True)  # Game title added

name_label = Text(text="Enter Your Name:", position=(0, 0.125), scale=2, color=color.white, origin=(0, 0))
name_input = InputField(default_value='', max_lines=1, position=(0, 0.075), scale=(0.4, 0.05))  # Input field is empty by default
go_button = Button(text='Go', color=color.azure, position=(0, -0.1), scale=(0.1, 0.05))

def start_game():
    global player_name, start_time, game_started
    player_name = name_input.text.strip()

    if not player_name:
        show_message("Please enter your name!", color.red)
        return

    # Hide startup screen elements
    destroy(name_input)
    destroy(go_button)
    destroy(name_label)  # Destroy the name_label when the game starts
    destroy(game_title)

    # Start the game logic
    start_time = time.time()
    game_started = True  # Set the game as started
    show_message(f"Welcome, {player_name}!", color.green)

go_button.on_click = start_game


player = Entity(model='wbc.obj', texture="White_Blood_Cell_Background_Textured.png",
                scale=(0.2, 0.2, 0.2), position=(0, 0, -5))
player.speed = 0.03

exit_button = Button(text='Exit', color=color.red, scale=(0.1, 0.05), position=(0.6, 0.45))
exit_button.on_click = application.quit

game_over_text = Text(text='', position=(0, 0), scale=3, color=color.yellow, origin=(0, 0), visible=False)
score_hit = 0
score_miss = 0

# White background boxes for readability
#white_box = Entity(model='quad', color=color.rgba(255, 255, 255, 50), scale=(0.43, 0.1), position=(-0.53, 0.4, 0.01), parent=camera.ui)

score_hit_text = Text(text=f'Targets Hit: {score_hit}', position=(-0.75, 0.45), scale=2, color=color.green)
score_miss_text = Text(text=f'Targets Missed: {score_miss}', position=(-0.75, 0.40), scale=2, color=color.white)

targets = []
rbcs = []
last_speed_increase_time = 0  # Tracks when the last speed increase occurred
target_speed = 0.032 #initial target speed
rbc_speed = 0.05  

game_duration = 80
start_time = None  

angleX, angleY, angleZ = 0, 0, 0

def imu_data_thread():
    """Fetch IMU data continuously in a separate thread."""
    global angleX, angleY, angleZ
    while True:
        imu_data = process_imu_data()
        if imu_data:
            try:
                angleX, angleY, angleZ = imu_data[0].item(), imu_data[1].item(), imu_data[2].item()
                #print(angleX, angleY)
            except (IndexError, AttributeError):
                continue  # Ignore errors if data is incomplete

threading.Thread(target=imu_data_thread, daemon=True).start()

def update_score():
    if game_started:
        score_hit_text.text = f'Targets Hit: {score_hit}'
        score_miss_text.text = f'Targets Missed: {score_miss}'

last_player_score = 0
leaderboard_display = None  # Track the leaderboard text object

def game_over():
    global score_hit, score_miss, last_player_score
    last_player_score = score_hit  # Store the last player's score
    save_last_score()
    game_over_text.text = f"Game Over!\nTargets Hit: {score_hit}\nTargets Missed: {score_miss}"
    game_over_text.visible = True
    display_leaderboard()
    player.disable()
    for target in targets:
        destroy(target)
    for rbc in rbcs:
        destroy(rbc)
    invoke(application.quit, delay=10)

def save_last_score():
    global last_player_score, player_name
    score_entry = f"{player_name},{last_player_score},{time.strftime('%Y-%m-%d %H:%M:%S')}\n"

    with open("leaderboard.txt", "a") as file:
        file.write(score_entry)

def load_leaderboard():
    scores = []
    try:
        with open("leaderboard.txt", "r") as file:
            for line in file:
                data = line.strip().split(',')
                if len(data) == 3:  # Ensure all entries have name, score, and timestamp
                    name, score, timestamp = data
                    scores.append((name, int(score), timestamp))
    except FileNotFoundError:
        pass  

    # Remove duplicate scores while keeping the latest entries
    seen_scores = set()
    unique_scores = []

    for name, score, timestamp in reversed(scores):
        if score not in seen_scores:
            seen_scores.add(score)
            unique_scores.append((name, score, timestamp))

    # Sort by score in descending order
    unique_scores.sort(key=lambda x: x[1], reverse=True)

    return unique_scores[:3]  # Return the top 3 scores


def display_leaderboard():
    global leaderboard_display

    if leaderboard_display:
        destroy(leaderboard_display)

    leaderboard = load_leaderboard()
    leaderboard_text = "Leaderboard:\n"
    for i, (name, score, timestamp) in enumerate(leaderboard, 1):
        leaderboard_text += f"{i}. {name} {score} hits ({timestamp})\n"

    leaderboard_display = Text(text=leaderboard_text, position=(0, -0.2), scale=1.5, color=color.white)
    leaderboard_display.visible = True

X_MIN, X_MAX = -5, 5
Y_MIN, Y_MAX = -3, 3
prev_x_dir, prev_y_dir = 0, 0
message_text = Text(text='', position=(0, 0), scale=2, color=color.white, origin=(0, 0))

# Show Message

def show_message(text, color=color.white, duration=2):
    message_text.text = text
    message_text.color = color
    message_text.visible = True  
    invoke(hide_message, delay=duration)

def hide_message():
    message_text.visible = False

def spawn_target():


    if len(targets) < 3:
        x = random.uniform(-3, 3)
        y = random.uniform(-2, 2)
        target = Entity(model='CoronaVirus.obj', texture='Corona.png',
                        scale=(0.2, 0.2, 0.2), position=(x, y, 10))  
        targets.append(target)
    
    invoke(spawn_target, delay=5 )


for _ in range(20):
    rbc = Entity(model='RBCsv3.obj', texture='text2.jpeg', 
                 scale=(1, 1, 1), 
                 position=(random.uniform(-3, 3), random.uniform(-2, 2), random.uniform(3, 8)))
    rbcs.append(rbc)

spawn_target()


movement_threshold = 3  
max_speed = 0.03  
slow_speed = 0.015 
base_speed = 0.04
slowdown_factor = 0.8
max_angle= 0


def update():
    #print(f"Frame Time: {time.dt:.4f} sec | FPS: {1/time.dt:.2f}")
    global score_hit, score_miss, start_time, prev_x_dir, prev_y_dir, target_speed, last_speed_increase_time
    if start_time is None:  
        start_time = time.time()  

    elapsed_time = time.time() - start_time  

    # Increase target speed every 30 seconds
    if elapsed_time - last_speed_increase_time >= 30:
        target_speed *= 1.50  # Increase speed by 50%
        last_speed_increase_time = elapsed_time  # Reset the timer
        show_message(f"New Level! Coronavirus Speed Increased", color.yellow)

    if elapsed_time >= game_duration:
        game_over()
        return
    

    def calculate_speedx(angle):
        """Scale speed based on tilt angle, with slow movement in specific ranges."""
        if abs(angle) < movement_threshold:
            return 0  

        # Slow movement if angle is in slow zones
        if -15 <= angle <= 0 or 0 <= angle <= 15:
            return slow_speed  
        else:
            speed = base_speed + ((abs(angle) - movement_threshold) / (max_angle - movement_threshold)) * (max_speed - base_speed)
        return min(speed, max_speed)  # Cap speed at max_speed

    def calculate_speedy(angle):
        """Scale speed based on tilt angle."""
        if abs(angle) < movement_threshold:
            return 0  # No movement in dead zone
        
        speed = base_speed + ((abs(angle) - movement_threshold) / (max_angle - movement_threshold)) * (max_speed - base_speed)
        return min(speed, max_speed)  # Cap speed at max_speed

    move_x, move_y = 0, 0
    x_dir, y_dir = 0, 0  

    if angleX > movement_threshold:
        move_x = calculate_speedx(angleX)  # Move RIGHT
        x_dir = 1  
    elif angleX < -movement_threshold:
        move_x = -calculate_speedx(angleX)  # Move LEFT 
        x_dir = -1

    if angleY > -movement_threshold:
        move_y = -calculate_speedy(angleY)  # Move down
        y_dir = -1
    elif angleY < movement_threshold:
        move_y = calculate_speedy(angleY)  # Move up
        y_dir = 1

    if x_dir != 0 and x_dir != prev_x_dir:  
        move_x *= slowdown_factor
    if y_dir != 0 and y_dir != prev_y_dir:  
        move_y *= slowdown_factor

    player.x += move_x
    player.y += move_y  

    prev_x_dir = x_dir
    prev_y_dir = y_dir

    # Constrain player movement within bounds
    player.y = max(min(player.y, Y_MAX), Y_MIN)
    player.x = max(min(player.x, X_MAX), X_MIN)

    # Move Targets
    if game_started:
        for target in targets[:]:
            target.z -= target_speed  
            if target.z < -6:  #how far away target is 
                score_miss += 1  
                show_message("Target Missed!", color.red) 
                update_score()
                targets.remove(target)
                destroy(target)

    # Check Collisions
    if game_started:
        for target in targets[:]:
            if abs(player.x - target.x) < 0.3 and abs(player.y - target.y) < 0.3 :
                score_hit += 1  

                success_phrases = [
                "Nice hit!", "Great shot!", "Awesome aim!", "Bullseye!", 
                "Direct hit!", "Boom! Nailed it!", "On target!", 
                "Excellent shot!", "Crushed it!", "Perfect strike!", 
                "You're unstoppable!", "Virus eradicated!", "Target neutralized!"
                ]

                def random_success_message():
                    return random.choice(success_phrases)

                show_message(random_success_message(), color.green)
                update_score()
                targets.remove(target)
                destroy(target)

    # Move RBCs
    for rbc in rbcs:
        rbc.x += random.uniform(-0.01, 0.01)
        rbc.y += random.uniform(-0.01, 0.01)
        rbc.z -= rbc_speed
        if rbc.z < -6:
            rbc.position = (random.uniform(-8, 8), random.uniform(-6, 6), random.uniform(3, 15))

app.run()