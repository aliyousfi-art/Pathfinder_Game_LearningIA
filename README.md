# PathFinder AI

A maze game where an AI learns the best path by itself.

## What it does

The agent starts at S and tries to reach E.
Every time it fails, it learns from its mistake.
After many tries, it finds and remembers the best path.

## How to run

```bash
python3 -m venv venv
source venv/bin/activate
pip install pygame
python pathfinder/Game.py
```

## Controls

- Arrow UP / DOWN : change speed
- R : reset the AI

## Built with

- Python
- Pygame
- Q-Learning
