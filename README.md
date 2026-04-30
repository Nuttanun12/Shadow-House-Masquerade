# 🕯️ Shadow House: Masquerade
### A Digital Board Game — Python Project

> A professional digital adaptation of the social deduction card game **Shadow House: Masquerade**, built with Python and PyQt6.

---

## 📖 Introduction

**Shadow House: Masquerade** is a social deduction card game set in a mysterious gothic manor. One player secretly holds the **Culprit** card — the murderer hiding among the guests. Other players take on roles such as Detective, Sheriff, Witness, Alibi, and more, working together (or against each other) to expose or protect the Culprit before the night is over.

### Game Features Implemented
- Full card-based gameplay with 10 unique role cards
- AI opponents with decision-making logic
- Target selection system for active cards (Detective, Toby, Sheriff, Witness)
- Protection mechanics (Alibi / Servant cards)
- Handcuff & immediate-arrest mechanic (Sheriff card)
- Witness peek — secretly view another player's hand
- Multi-round scoring system (first to 5 points wins)
- Persistent game history and leaderboard via SQLite database
- Fully themed gothic GUI with animated card widgets

### Objective
Identify the Culprit before they escape — or, if you are the Culprit, play your card last without being caught.

---

## 🎮 How to Play

### Rules
- Each player is dealt **4 cards** per round.
- On your turn, **click a card** in your hand to play it.
- Cards that require a target (🔍 Detective, 🐕 Toby, 🔒 Sheriff, 👁 Witness) will open a **target selection dialog**.
- The round ends when:
  - A **Detective** or **Toby** correctly identifies the Culprit.
  - The **Culprit** card is played as the last card.
  - The **Sheriff** places handcuffs on the Culprit.
- The game ends when any player reaches **5 points**.

### Card Reference

| Card | Effect |
|---|---|
| **Culprit** | You are the murderer. Play this last to win. If caught, you lose. |
| **Accomplice** | You win when the Culprit wins. |
| **Detective** | Point at a player — if they hold the Culprit, the round ends. |
| **Toby (Dog)** | Same as Detective but with a canine nose. |
| **Sheriff** | Handcuff a player. If they hold the Culprit, they are arrested immediately. |
| **Witness** | Secretly peek at another player's entire hand. |
| **Alibi** | Protect yourself — no one can target you until your next turn. |
| **Servant** | Same protection as Alibi. |
| **First on Scene** | Holder goes first this round. |
| **Citizen** | Swap your top card with the next player's top card. |

### Winning Conditions
- **Innocents / Detective win** a round: arresting player **+2 pts**, others **+1 pt**
- **Culprit escapes**: Culprit **+2 pts**, Accomplices **+1 pt**
- **Game winner**: first player to reach **5 points**

---

## 🗂️ File Structure

```
ShadowHouseMasquerade/
│
├── main.py                  # Entry point — launches the application
├── requirements.txt         # Python dependencies
├── setup_env.sh             # macOS/Linux environment setup script
├── setup_env.bat            # Windows environment setup script
├── game_records.db          # SQLite database (auto-created on first run)
│
├── game/                    # Core game logic
│   ├── __init__.py
│   ├── models.py            # Data models: RoleType, Card, Player
│   └── engine.py            # GameEngine — deck, turns, effects, scoring, AI
│
├── ui/                      # GUI layer (PyQt6)
│   ├── __init__.py
│   ├── main_window.py       # MainWindow — screen stack & navigation
│   ├── components/
│   │   ├── __init__.py
│   │   └── card.py          # CardWidget — animated card with gradient face/back
│   └── screens/
│       ├── __init__.py
│       ├── menu.py          # MenuScreen — player setup & navigation
│       ├── board.py         # BoardScreen — gameplay, dialogs, AI turns
│       └── stats.py         # StatsScreen — leaderboard & game history tabs
│
├── storage/                 # Data persistence
│   ├── __init__.py
│   └── database.py          # DatabaseManager — SQLite CRUD operations
│
├── utils/                   # Shared utilities
│   ├── __init__.py
│   └── helpers.py           # Resource paths, timestamp formatting, validation
│
└── resources/               # Static assets
    ├── images/
    │   ├── menu_bg.png
    │   ├── board_bg.png
    │   └── card_back.png
    └── fonts/
```

---

## ⚙️ How to Run from Scratch

### Prerequisites
- Python **3.10+** installed
- `pip` available

### Step 1 — Clone / open the project
```bash
# If downloaded as a zip, extract it.
# Navigate into the project folder:
cd ShadowHouseMasquerade
```

### Step 2 — Create & activate a virtual environment

**macOS / Linux:**
```bash
bash setup_env.sh
source venv/bin/activate
```

**Windows:**
```cmd
setup_env.bat
venv\Scripts\activate
```

> Or manually:
> ```bash
> python3 -m venv venv
> source venv/bin/activate        # macOS/Linux
> pip install --upgrade pip
> pip install -r requirements.txt
> ```

### Step 3 — Run the game
```bash
python main.py
```

The game window (1100 × 750) will open. No additional configuration is required.

---

## 🧩 Coding Features

### Major Classes

| Class | File | Responsibility |
|---|---|---|
| `RoleType` | `game/models.py` | Enum of all 10 card roles |
| `Card` | `game/models.py` | Holds role, name, description, display colors |
| `Player` | `game/models.py` | Tracks hand, score, handcuff & protection state |
| `GameEngine` | `game/engine.py` | Deck creation, turn flow, card effects, scoring, AI |
| `DatabaseManager` | `storage/database.py` | SQLite init, record_game, update_player_stats, get_leaderboard, get_history |
| `MainWindow` | `ui/main_window.py` | QStackedWidget screen manager |
| `MenuScreen` | `ui/screens/menu.py` | Name input, AI count, navigation |
| `BoardScreen` | `ui/screens/board.py` | Main gameplay screen, dialogs, AI timer |
| `StatsScreen` | `ui/screens/stats.py` | Leaderboard & history tabs |
| `CardWidget` | `ui/components/card.py` | Animated card — gradient face/back, hover lift |
| `TargetDialog` | `ui/screens/board.py` | Target player selection popup |
| `WitnessDialog` | `ui/screens/board.py` | Reveals peeked player's hand |
| `PlayerPanel` | `ui/screens/board.py` | Opponent status panel (cards, badges, score) |

### Key Algorithms

- **Deck generation** (`engine._create_deck`): Builds a role-based starter set per player count, then fills remaining slots with filler roles to reach `num_players × 4` cards.
- **AI decision** (`engine.ai_play`): Avoids playing the Culprit card when alternatives exist; targets unprotected players with aggressive cards.
- **Immediate handcuff-arrest** (`engine._resolve_effect` — Sheriff): If the Sheriff targets the Culprit, the round ends on the spot, preventing the escape mechanic.
- **Witness flow**: The board screen captures a snapshot of the target's hand *before* the card is consumed, then displays it via `WitnessDialog` after `refresh_board`.

---

## 🔄 Data Flow

```
Player Input (mouse click on card)
        │
        ▼
  BoardScreen.card_clicked()
        │  (optional) TargetDialog shown → user picks target
        ▼
  GameEngine.play_card(player_idx, card_idx, target_idx)
        │
        ▼
  GameEngine._resolve_effect()   ← applies card rule
        │
        ├─ "ROUND_END"  → _end_round() → scoring → _check_game_over()
        │                                   │
        │                                   ├─ game over → _save_to_db() → DatabaseManager
        │                                   └─ continue  → setup_round()
        │
        ├─ "WITNESS"    → board captures hand snapshot
        │
        └─ "CONTINUE"   → advance_turn()
                │
                ▼
        BoardScreen.refresh_board()   ← redraws UI
                │
                ├─ updates round/turn labels
                ├─ refreshes PlayerPanels
                ├─ rebuilds game log
                ├─ redraws human hand (CardWidgets)
                └─ triggers QTimer → _ai_turn() if AI's turn
```

---

## 🗄️ Database Schema

**`player_stats`**
| Column | Type | Description |
|---|---|---|
| player_name | TEXT PK | Unique player identifier |
| games_played | INTEGER | Total completed games |
| wins | INTEGER | Total wins |
| total_score | INTEGER | Cumulative score across all games |

**`game_history`**
| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-increment game ID |
| date_played | TIMESTAMP | Recorded automatically |
| winner_name | TEXT | Name of the winning player |
| final_scores | TEXT | JSON: `{"Player": score, ...}` |

---

## 👥 Developer Team

| Name | Role |
|---|---|
| Member 1 | Game Logic & Engine |
| Member 2 | GUI & Database |

---

## 📦 Dependencies

```
PyQt6==6.6.1
PyQt6-Qt6==6.6.1
PyQt6-sip==13.6.0
```

All dependencies are standard and installable via `pip` with no system-level requirements beyond Python 3.10+.
