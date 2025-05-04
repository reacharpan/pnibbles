import os # Add this import
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse # Add FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import random
from db import init_db, save_score, get_top_scores

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SnakeGame")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
init_db()

# Define path to the frontend directory relative to this script
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
index_html_path = os.path.join(frontend_dir, "index.html")

# Game state
class SnakeGame:
    def __init__(self):
        self.board_size = (36, 20)  # 16:9 ratio with height of 20 cells
        self.players = {}
        self.scores = {}
        self.food = self.generate_food()
        self.game_over = {}
        self.player_names = {}  # Store player names
        logger.debug(f"[DEBUG] SnakeGame initialized with board_size={self.board_size}, food={self.food}")  # BREAKPOINT: Game initialization

    def generate_food(self):
        food_pos = (random.randint(0, self.board_size[0] - 1),
                    random.randint(0, self.board_size[1] - 1))
        logger.debug(f"[DEBUG] Generated food at {food_pos}")  # BREAKPOINT: Food generation
        return food_pos

    def add_player(self, player_id, player_name):
        # Start snake in the middle of the left side
        start_x = 5
        start_y = self.board_size[1] // 2
        self.players[player_id] = [(start_x, start_y)]
        self.scores[player_id] = 0
        self.game_over[player_id] = False
        self.player_names[player_id] = player_name
        logger.debug(f"[DEBUG] Added player {player_name} ({player_id}) at position ({start_x}, {start_y})")  # BREAKPOINT: Player addition

    def check_food_collision(self, head):
        return head == self.food

    def check_self_collision(self, player_id, new_head):
        # Check if the new head position collides with any part of the snake's body
        # Skip the last segment since it will move out of the way
        snake_body = self.players[player_id][:-1]
        return new_head in snake_body

    def reset_player(self, player_id):
        # Start snake in the middle of the left side
        start_x = 5
        start_y = self.board_size[1] // 2
        self.players[player_id] = [(start_x, start_y)]
        self.scores[player_id] = 0
        self.game_over[player_id] = False

    def move_player(self, player_id, direction):
        logger.debug(f"[DEBUG] move_player called for {player_id} with direction={direction}")  # BREAKPOINT: Move player
        if player_id not in self.players or self.game_over.get(player_id, False):
            logger.debug(f"[DEBUG] Player {player_id} not found or game over.")
            return

        head = self.players[player_id][0]
        if direction == "up":
            new_head = (head[0], head[1] - 1)
        elif direction == "down":
            new_head = (head[0], head[1] + 1)
        elif direction == "left":
            new_head = (head[0] - 1, head[1])
        elif direction == "right":
            new_head = (head[0] + 1, head[1])
        else:
            logger.debug(f"[DEBUG] Invalid direction: {direction}")
            return

        logger.debug(f"[DEBUG] Player {player_id} moving from {head} to {new_head}")

        # Check for wall collision
        if (new_head[0] < 0 or new_head[0] >= self.board_size[0] or
            new_head[1] < 0 or new_head[1] >= self.board_size[1]):
            self.game_over[player_id] = True
            logger.debug(f"[DEBUG] Player {player_id} hit wall at {new_head}")
            return

        # Check for self collision
        if self.check_self_collision(player_id, new_head):
            self.game_over[player_id] = True
            logger.debug(f"[DEBUG] Player {player_id} collided with self at {new_head}")
            return

        # Check if snake ate food
        if self.check_food_collision(new_head):
            # Don't remove the tail - snake grows
            self.players[player_id] = [new_head] + self.players[player_id]
            # Increment score
            self.scores[player_id] += 1
            # Generate new food position
            self.food = self.generate_food()
            logger.debug(f"[DEBUG] Player {player_id} ate food at {new_head}, new score: {self.scores[player_id]}")
        else:
            # Normal movement - remove tail
            self.players[player_id] = [new_head] + self.players[player_id][:-1]

    def get_state(self):
        # Filter out players who are marked as game_over
        active_players = {
            pid: segments for pid, segments in self.players.items()
            if not self.game_over.get(pid, False)
        }
        return {
            "players": active_players, # Return only active players
            "food": self.food,
            "board_size": self.board_size,
            "scores": self.scores, # Keep sending all scores
            "game_over": self.game_over # Keep sending all game_over statuses
        }

# Initialize game
game = SnakeGame()

@app.get("/")
async def get_index(): # Renamed function for clarity
    if os.path.exists(index_html_path):
        # Add no-cache headers
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        return FileResponse(index_html_path, headers=headers)
    else:
        # Fallback or error if index.html is not found
        logger.error(f"Frontend index.html not found at expected path: {index_html_path}")
        return HTMLResponse("<h1>Error: Frontend index.html not found</h1>", status_code=404)

@app.get("/top-scores")
async def get_high_scores():
    return get_top_scores()

@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    await websocket.accept()
    logger.debug(f"[DEBUG] WebSocket connection accepted for player_id={player_id}")  # BREAKPOINT: WebSocket connect
    
    # Wait for player name
    try:
        data = await websocket.receive_text()
        player_info = json.loads(data)
        player_name = player_info.get("player_name", f"Player_{player_id}")
        
        # Initialize player
        game.add_player(player_id, player_name)
        logger.info(f"Player {player_name} ({player_id}) connected.")
        
        # Send initial game state
        await websocket.send_text(json.dumps(game.get_state()))
        logger.debug(f"[DEBUG] Sent initial game state to player {player_id}")
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.debug(f"[DEBUG] Received message from player {player_id}: {message}")
            
            if "direction" in message:
                game.move_player(player_id, message["direction"])
                
                # Check if game just ended
                if game.game_over.get(player_id, False):
                    final_score = game.scores[player_id]
                    is_top_10 = save_score(game.player_names[player_id], final_score)
                    top_scores = get_top_scores()
                    logger.debug(f"[DEBUG] Player {player_id} game over. Final score: {final_score}")
                    
                    # Send game over message with high score info
                    await websocket.send_text(json.dumps({
                        **game.get_state(),
                        "is_top_10": is_top_10,
                        "top_scores": top_scores
                    }))
                else:
                    # Send regular game state
                    await websocket.send_text(json.dumps(game.get_state()))
                    logger.debug(f"[DEBUG] Sent updated game state to player {player_id}")
    except WebSocketDisconnect:
        logger.info(f"Player {game.player_names.get(player_id, player_id)} disconnected.")
        if player_id in game.players:
            del game.players[player_id]
            del game.scores[player_id]
            del game.game_over[player_id]
            del game.player_names[player_id]