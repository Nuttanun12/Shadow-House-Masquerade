# Shadow House: Masquerade - Digital Board Game

A professional digital adaptation of the social deduction board game "Shadow House: Masquerade", built with Python and PyQt6.

## Features
- **Authentic Gameplay**: Implements core mechanics of the original card game.
- **AI Opponents**: Play against 2-7 computer-controlled players.
- **Professional GUI**: Mysterious gothic-themed interface with high-quality assets.
- **Persistence**: Tracks player statistics and game history using SQLite.
- **Modular Design**: Clean code structure following professional standards.

## Project Structure
- `game/`: Core game logic and engine.
- `ui/`: GUI implementation using PyQt6.
- `storage/`: Database management for records.
- `resources/`: Images and visual assets.

## How to Run

### 1. Requirements
Ensure you have Python 3.8+ installed.

### 2. Setup Environment
Run the setup script for your platform to create a virtual environment and install dependencies:

**macOS / Linux:**
```bash
bash setup_env.sh
```

**Windows:**
```cmd
setup_env.bat
```

### 3. Run the Game
Activate the virtual environment and launch the application:

**macOS / Linux:**
```bash
source venv/bin/activate
python main.py
```

**Windows:**
```cmd
venv\Scripts\activate
python main.py
```

## How to Play
1. Enter your name and select the number of AI players.
2. The goal is to identify the **Culprit** (if you are a Detective/Innocent) or stay hidden (if you are the Culprit).
3. On your turn, click a card in your hand to play it.
4. Follow the card's effect to gather information or manipulate the game state.
5. The first player to reach 5 points wins!

## Developer Team
- [Member 1]
- [Member 2]
