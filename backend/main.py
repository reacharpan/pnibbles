from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
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

# Game state
class SnakeGame:
    def __init__(self):
        self.board_size = (36, 20)  # 16:9 ratio with height of 20 cells
        self.players = {}
        self.scores = {}
        self.food = self.generate_food()
        self.game_over = {}
        self.player_names = {}  # Store player names

    def generate_food(self):
        return (random.randint(0, self.board_size[0] - 1),
                random.randint(0, self.board_size[1] - 1))

    def add_player(self, player_id, player_name):
        # Start snake in the middle of the left side
        start_x = 5
        start_y = self.board_size[1] // 2
        self.players[player_id] = [(start_x, start_y)]
        self.scores[player_id] = 0
        self.game_over[player_id] = False
        self.player_names[player_id] = player_name

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
        if player_id not in self.players or self.game_over.get(player_id, False):
            return

        head = self.players[player_id][0]
        if direction == "up":
            new_head = (head[0], (head[1] - 1) % self.board_size[1])
        elif direction == "down":
            new_head = (head[0], (head[1] + 1) % self.board_size[1])
        elif direction == "left":
            new_head = ((head[0] - 1) % self.board_size[0], head[1])
        elif direction == "right":
            new_head = ((head[0] + 1) % self.board_size[0], head[1])
        else:
            return

        # Check for self collision
        if self.check_self_collision(player_id, new_head):
            self.game_over[player_id] = True
            return

        # Check if snake ate food
        if self.check_food_collision(new_head):
            # Don't remove the tail - snake grows
            self.players[player_id] = [new_head] + self.players[player_id]
            # Increment score
            self.scores[player_id] += 1
            # Generate new food position
            self.food = self.generate_food()
        else:
            # Normal movement - remove tail
            self.players[player_id] = [new_head] + self.players[player_id][:-1]

    def get_state(self):
        return {
            "players": self.players,
            "food": self.food,
            "board_size": self.board_size,
            "scores": self.scores,
            "game_over": self.game_over
        }

# Initialize game
game = SnakeGame()

@app.get("/")
async def get():
    return HTMLResponse("<h1>Snake Game Backend</h1>")

@app.get("/top-scores")
async def get_high_scores():
    return get_top_scores()

@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    await websocket.accept()
    
    # Wait for player name
    try:
        data = await websocket.receive_text()
        player_info = json.loads(data)
        player_name = player_info.get("player_name", f"Player_{player_id}")
        
        # Initialize player
        game.add_player(player_id, player_name)
        logger.info(f"Player {player_name} ({player_id}) connected.")
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if "direction" in message:
                game.move_player(player_id, message["direction"])
                
                # Check if game just ended
                if game.game_over.get(player_id, False):
                    final_score = game.scores[player_id]
                    is_top_10 = save_score(game.player_names[player_id], final_score)
                    top_scores = get_top_scores()
                    
                    # Send game over message with high score info
                    await websocket.send_text(json.dumps({
                        **game.get_state(),
                        "is_top_10": is_top_10,
                        "top_scores": top_scores
                    }))
                else:
                    # Send regular game state
                    await websocket.send_text(json.dumps(game.get_state()))
                    
    except WebSocketDisconnect:
        logger.info(f"Player {game.player_names.get(player_id, player_id)} disconnected.")
        if player_id in game.players:
            del game.players[player_id]
            del game.scores[player_id]
            del game.game_over[player_id]
            del game.player_names[player_id]