# Mini Arcade

Mini Arcade is a small four-game collection built with Python and Pygame. The
main application owns one 1000 × 700 window and a single event loop; games are
created and discarded as the player navigates from the graphical menu.

## Games

- **Tic-Tac-Toe** — two-player local board game with win and draw detection.
- **Rock Paper Scissors** — play against the computer and track the score.
- **Memory Match** — find eight card pairs on a randomized 4 × 4 board.
- **Snake** — guide the growing snake, collect food, and avoid collisions.

## Technology

- Python 3.10 or newer
- Pygame Community Edition (`pygame-ce`)
- Python standard library for game logic and tests

## Install and run

Create and activate a virtual environment if desired, then install the pinned
dependency and launch the application:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Use the mouse for the menu and Tic-Tac-Toe, Rock Paper Scissors, and Memory
Match. Snake uses the arrow keys or WASD. Press **Escape** in any game to return
to the menu. The Exit button or window close button ends the application.

Run the automated logic and integration tests with:

```powershell
python -m unittest discover -s tests -v
```

## Project structure

```text
Mini-arcade/
├── main.py
├── src/
│   ├── menu/main_menu.py
│   ├── games/
│   │   ├── tic_tac_toe/game.py
│   │   ├── rock_paper_scissors/game.py
│   │   ├── memory_match/game.py
│   │   └── snake/game.py
│   └── utils/
│       ├── constants.py
│       └── helpers.py
├── tests/
├── requirements.txt
└── README.md
```

Each game follows the same interface: `handle_event(event)` handles input and
returns `"menu"` when navigation is requested, `update(dt_ms)` advances
time-based logic, and `draw(screen)` renders to the shared surface. The main
application handles window events and Pygame initialization and shutdown.

## Team contributions

This repository is structured for a four-person student team. Assign game
implementation, shared menu/UI, testing, and documentation responsibilities
among team members and record names/contributions here.

## Known limitations

- Tic-Tac-Toe is local two-player; there is no computer opponent.
- The games use vector shapes and text instead of external art or sound assets.
- No screenshots have been added yet.
