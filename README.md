# pnibbles v1.0.0

A modern multiplayer Snake game with real-time backend and customizable gameplay.

![version](https://img.shields.io/badge/version-v1.0.0-blue)

## Features (v1.0.0)
- Multiplayer real-time Snake gameplay
- Playable with or without obstacles (white blocks)
- Responsive, modern UI using Phaser.js
- Score display inside the game board
- Restart game by pressing 'R' after game over
- Food never appears on obstacles
- WebSocket backend (FastAPI) for real-time updates
- Game mode selection (with/without obstacles)

## Code Structure

### Frontend
- **Location:** `frontend/`
- **Tech:** HTML, JavaScript (Phaser.js)
- **Features:**
  - Game rendering and logic
  - UI for mode selection
  - Handles user input and game state

### Backend
- **Location:** `backend/`
- **Tech:** Python (FastAPI, WebSocket)
- **Features:**
  - Manages multiplayer game state
  - Real-time updates via WebSocket
  - Handles player connections and scores

## Getting Started

1. Run the backend server (see `backend/` for FastAPI setup).
2. Serve the frontend (see `frontend/` for static files).
3. Open the frontend in your browser and select your preferred game mode.

## Documentation
- Sphinx documentation is available in `backend/docs/` and reflects both backend and frontend integration.

---

A 1-2 player snake game with a React frontend and FastAPI backend.

## Setup

### Backend
1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Start a simple HTTP server (using Python):
   ```
   # If you're using Python 3
   python -m http.server 3000
   # If you're using Python 2
   python -m SimpleHTTPServer 3000
   ```

## API Documentation
1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Build the documentation:
   ```
   cd docs
   make html
   ```

3. View the documentation:
   - Open `backend/docs/_build/html/index.html` in your web browser
   - You'll find complete API reference, database schema, and visual diagrams of the game flow

## Playing the Game
1. Open your web browser and go to `http://localhost:3000`
2. Use the arrow keys to control your snake
3. Collect the food (red dots) to grow your snake
4. Avoid hitting the walls or your own snake's body

The game supports multiplayer, so multiple players can connect to the same game server simultaneously!
