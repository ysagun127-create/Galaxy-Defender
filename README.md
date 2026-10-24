🚀 Galaxy Defender

A fast-paced 2D space shooter built with Python and Pygame as an MCA Mini Project. Pilot your spaceship, blast alien invaders, dodge asteroids, and climb the high-score table. Scores are saved to a CSV file and can be viewed in a built-in analytics dashboard.

Features
Smooth spaceship movement with normalized diagonal speed (NumPy vectors)
Alien enemies and drifting asteroids that spawn faster as you level up
Random power-ups dropped by destroyed enemies (restore a life, up to 5)
Level progression every 100 points
Brief invincibility after taking a hit
Scrolling starfield background
Game states: Menu, Playing, Paused, Game Over
Automatic score saving to galaxy_scores.csv (Pandas), with the Top 5 players printed in the terminal
Analytics dashboard (Matplotlib): top player scores and score distribution, plus average and highest score
Tech Stack
Library	Purpose
pygame	Game window, graphics, input, game loop
numpy	Player movement and score statistics
pandas	Saving and sorting scores in CSV
matplotlib	Analytics charts
Requirements
Python 3.8 or higher
Installation
Clone the repository:
   git clone https://github.com/ysagun127-create/Galaxy-Defender.git
   cd Galaxy-Defender
Install the dependencies:
   pip install pygame numpy pandas matplotlib
How to Run
python galaxy_defender.py

You will be asked to enter your player name in the terminal, then the game window opens.

Controls
Key	Action
Arrow keys / W A S D	Move the spaceship
SPACE (hold)	Shoot
P	Pause / resume
ENTER	Start game (menu)
A	View analytics (menu / game over)
R	Play again (game over)
ESC	Back to menu / quit from menu
Gameplay
Shoot enemies to earn 10 points each.
Colliding with an enemy or asteroid costs 1 life. You start with 3 lives.
Green orbs (power-ups) restore a life, up to a maximum of 5.
The game ends when your lives reach 0, and your score is saved automatically.
Project Structure
Galaxy-Defender/
├── galaxy_defender.py   # Main game code
├── galaxy_scores.csv    # Saved player scores (Player, Score, Level)
└── README.md
Author

Sagun Yadav MCA, Chandigarh University GitHub: @ysagun127-create
