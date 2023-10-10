import pygame
import sys
import os
import csv
import time
from pygame import mixer

# Initialize Pygame
pygame.init()

# Initialize the mixer module
mixer.init()

# Set up some constants
WIDTH, HEIGHT = 1200, 800  # Increase the size of the window
PADDING = 20  # Padding around each poster
SONG_NAMES_FILE = "songs.txt"
SONG_POSTERS_DIR = "posters"
SONG_NOTES_DIR = "notes"  # Directory containing the note data for each song
BACKGROUND_IMAGE = "assets/background.jpg"  # Path to your background image
HITSOUND = "assets/hitsound.wav" # Path to your hitsound file

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load the background image
background = pygame.image.load(BACKGROUND_IMAGE)
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Get a list of all song posters in the directory, sorted by filename
SONG_POSTERS = sorted([name for name in os.listdir(SONG_POSTERS_DIR) if name.endswith('.png')], key=lambda x: int(x.split(' - ')[0]))

# Add the directory path to each poster filename
SONG_POSTERS = [os.path.join(SONG_POSTERS_DIR, name) for name in SONG_POSTERS]

# Load song names from a file, sorted by song name, and remove numbering
with open(SONG_NAMES_FILE, 'r') as f:
    SONG_NAMES = sorted([line.strip() for line in f], key=lambda x: int(x.split(' - ')[0]))

# Load and scale the song posters
posters = [pygame.transform.scale(pygame.image.load(name), (WIDTH // len(SONG_POSTERS) - 2 * PADDING, HEIGHT // 2 - PADDING)) for name in SONG_POSTERS]

# Load note data from a CSV file for each song
def load_notes(song_number):
    with open(os.path.join(SONG_NOTES_DIR, f"{song_number} - notes.csv"), 'r') as f:
        reader = csv.DictReader(f)
        notes = [row for row in reader]  # Consume the iterator and convert it to a list
    print(notes)  # Print the notes for debugging purposes
    return notes

def draw_menu():
    # Draw the background image
    screen.blit(background, (0, 0))
    
    for i, (name, poster) in enumerate(zip(SONG_NAMES, posters)):
        # Calculate the position of the poster taking into account the padding
        pos_x = i * (WIDTH // len(SONG_NAMES)) + PADDING
        pos_y = HEIGHT // 2 + PADDING
        
        # Draw the poster
        screen.blit(poster, (pos_x, pos_y))
        
        # Create a font object
        font = pygame.font.Font(None, 36)
        
        # Render the song name
        text = font.render(' - '.join(name.split(' - ')[1:]), True, (255, 255, 255))
        
        # Draw the song name above the poster
        screen.blit(text, (pos_x, pos_y - text.get_height() - PADDING))

    # Debug statement to check if posters are being displayed
    print("Posters displayed on the screen")  # Add this line

def draw_lanes():
    # Draw lanes on the screen
    num_lanes = 4
    lane_width = 50  # Width of each lane
    lane_color = (100, 100, 100)  # Gray color for the lanes

    for i in range(num_lanes):
        # Calculate the position and dimensions of each lane
        lane_x = (WIDTH - (lane_width * num_lanes)) // 2 + (lane_width * i)
        lane_y = HEIGHT // 2
        lane_height = HEIGHT // 2

        # Draw the lane
        pygame.draw.rect(screen, lane_color, (lane_x, lane_y, lane_width, lane_height))


# Game loop
running = True
game_started = False  # Add a flag to track if the game has started
notes = None  # Initialize notes to None
start_time = 0  # Initialize start_time to 0
current_note_index = 0  # Add this variable to track the current note index
score = 0  # Add a variable to track the score
countdown_start_time = 0  # Initialize countdown_start_time to 0
countdown_duration = 5  # Duration of the countdown in seconds

# Define a dictionary to map key presses to lane numbers
key_to_lane = {
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_4: 4,
}

# Initialize a dictionary to track which lanes are currently pressed
lanes_pressed = {1: False, 2: False, 3: False, 4: False}

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Check for mouse click events only if the game hasn't started yet
        if event.type == pygame.MOUSEBUTTONDOWN and not game_started:
            x, y = pygame.mouse.get_pos()
            print(f"Mouse clicked at ({x}, {y})")

            for i, (name, poster) in enumerate(zip(SONG_NAMES, posters)):
                pos_x = i * (WIDTH // len(SONG_NAMES)) + PADDING
                pos_y = HEIGHT // 2 + PADDING

                if pos_x <= x <= pos_x + poster.get_width() and pos_y <= y <= pos_y + poster.get_height():
                    print(f"Poster {i+1} clicked")
                    notes = load_notes(i+1)
                    game_started = True
                    start_time = time.time()
                    current_note_index = 0
                    score = 0  # Reset the score when starting a new song
                    countdown_start_time = time.time()  # Start the countdown timer

    current_time = time.time() - start_time

    if game_started:
        while current_note_index < len(notes):
            note = notes[current_note_index]
            note_time = float(note['time'])

            # Check if the current note should be pressed
            if current_time >= note_time:
                lane = int(note['lane'])
                note_type = note['type']

                if lanes_pressed.get(lane, False):
                    # Check if the corresponding lane key is pressed
                    if note_type == 'tap':
                        # Handle tap note logic (e.g., increase score)
                        if abs(current_time - note_time) <= 0.5:  # Adjust the timing window as needed
                            score += 100
                            print(f"Note at time {note_time} - Lane {lane} - TAP - Hit! Score: {score}")
                        else:
                            print(f"Note at time {note_time} - Lane {lane} - TAP - Missed")

                    elif note_type == 'hold':
                        # Handle hold note logic
                        if abs(current_time - note_time) <= 0.5:  # Adjust the timing window as needed
                            if 'hold_start' not in note:
                                note['hold_start'] = current_time

                            # Check if the hold note is held for at least 1 second
                            if current_time - note['hold_start'] >= 1.0:
                                score += 200
                                print(f"Note at time {note_time} - Lane {lane} - HOLD - Held! Score: {score}")
                        else:
                            print(f"Note at time {note_time} - Lane {lane} - HOLD - Missed")

                current_note_index += 1
            else:
                break
    draw_menu()
    if countdown_start_time > 0:
        # Calculate the remaining time in the countdown
        countdown_time = countdown_duration - (time.time() - countdown_start_time)
        if countdown_time <= 0:
            countdown_start_time = 0
            # Clear the screen and draw the menu again
            screen.fill((0, 0, 0))  # Clear the screen with a black background
            draw_lanes()  # Redraw the menu with lanes
        else:
            # Display the countdown timer on the screen
            font = pygame.font.Font(None, 72)
            text = font.render(str(int(countdown_time)), True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

    pygame.display.flip()
