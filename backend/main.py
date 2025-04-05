from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SnakeGame")

app = FastAPI()

# Game state
class SnakeGame:
    def __init__(self):
        self.players = {}
        self.food = (5, 5)
        self.board_size = (20, 20)

    def add_player(self, player_id):
        self.players[player_id] = [(0, 0)]

    def move_player(self, player_id, direction):
        if player_id not in self.players:
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
            return

        self.players[player_id] = [new_head] + self.players[player_id][:-1]

    def get_state(self):
        return {
            "players": self.players,
            "food": self.food,
            "board_size": self.board_size
        }

# Initialize game
game = SnakeGame()

@app.get("/")
async def get():
    return HTMLResponse("<h1>Snake Game Backend</h1>")

@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str):
    logger.info(f"Player {player_id} connected.")
    await websocket.accept()
    game.add_player(player_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received data from player {player_id}: {data}")
            message = json.loads(data)
            if "direction" in message:
                game.move_player(player_id, message["direction"])

            # Send updated game state to the client
            state = game.get_state()
            logger.info(f"Sending game state to player {player_id}: {state}")
            await websocket.send_text(json.dumps(state))
    except WebSocketDisconnect:
        logger.info(f"Player {player_id} disconnected.")
        del game.players[player_id]