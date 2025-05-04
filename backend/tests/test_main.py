# backend/tests/test_main.py
import pytest
import pytest_asyncio
from httpx import AsyncClient
import httpx
from fastapi import FastAPI
# from fastapi.testclient import TestClient # TestClient is for sync tests
from websockets.client import connect as websocket_connect
import json
import sqlite3
import os

# Import the FastAPI app instance from your main module
# Adjust the import path if your main.py is structured differently
from ..main import app as main_app
from ..main import game # Import the game instance for direct manipulation if needed
from ..db import init_db, get_top_scores, save_score # Import db functions

# Use httpx for async testing
BASE_URL = "http://testserver" # Standard base URL for TestClient
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'scores.db') # Adjust path relative to test file

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """Fixture to initialize and clean up the test database for each test."""
    # Use a separate test database or ensure cleanup
    # For simplicity, we'll re-initialize the existing one,
    # but a dedicated test DB is better practice.
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    init_db()
    # Optionally clear scores before each test if needed
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM high_scores")
    conn.commit()
    conn.close()
    yield # Test runs here
    # Cleanup after test if necessary (already handled by next test's init)

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Provides an async test client for the FastAPI app."""
    async with AsyncClient(transport=httpx.ASGITransport(app=main_app), base_url=BASE_URL) as client:
        yield client

@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    """Test the root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "<h1>Snake Game Backend</h1>" in response.text

@pytest.mark.asyncio
async def test_get_top_scores_empty(client: AsyncClient):
    """Test getting top scores when the database is empty."""
    response = await client.get("/top-scores")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_top_scores_with_data(client: AsyncClient):
    """Test getting top scores after adding some scores."""
    # Add some scores directly via db functions for testing
    save_score("Tester1", 10)
    save_score("Tester2", 5)
    save_score("Tester3", 15)

    response = await client.get("/top-scores")
    assert response.status_code == 200
    scores = response.json()
    assert len(scores) == 3
    assert scores[0]["player_name"] == "Tester3"
    assert scores[0]["score"] == 15
    assert scores[1]["player_name"] == "Tester1"
    assert scores[2]["player_name"] == "Tester2"

# Note: Testing WebSockets with TestClient is complex.
# A basic connection test might look like this, but requires running a test server.
# For more robust WebSocket testing, consider libraries like `pytest-fastapi-deps`
# or structuring tests to directly call the websocket endpoint function.

# Example of a more direct WebSocket test (might need adjustments)
@pytest.mark.asyncio
async def test_websocket_connection():
    """Test basic WebSocket connection and initial message."""
    test_player_id = "test_ws_player_123"
    test_player_name = "WS_Tester"
    # Requires the server to be running or use TestServer capabilities
    # This example assumes direct connection capability for simplicity
    try:
        # Use ws://localhost:8000 if running server separately for testing
        # Or adapt if using TestServer context manager
        # Using 127.0.0.1 instead of localhost can sometimes help
        async with websocket_connect(f"ws://127.0.0.1:8000/ws/{test_player_id}") as websocket:
            # Send player name
            await websocket.send(json.dumps({"player_name": test_player_name}))
            # Receive initial game state
            response = await websocket.recv()
            state = json.loads(response)
            assert "players" in state
            assert "food" in state
            assert "board_size" in state
            assert test_player_id in state["players"] # Check if player was added
            assert state["players"][test_player_id] is not None
    except ConnectionRefusedError:
        pytest.skip("WebSocket test requires a running server or TestServer setup.")
    except Exception as e:
        pytest.fail(f"WebSocket test failed: {e}")

# Add more tests for game logic (move_player, collisions, game over)
# by potentially calling the game methods directly or via WebSocket interactions.

# Example test for game logic (requires careful state setup)
@pytest.mark.asyncio
async def test_move_player_logic():
    """Test the move_player logic directly."""
    player_id = "test_logic_player"
    player_name = "LogicTester"
    game.add_player(player_id, player_name)

    initial_pos = game.players[player_id][0]
    game.move_player(player_id, "right")
    new_pos = game.players[player_id][0]

    assert new_pos == (initial_pos[0] + 1, initial_pos[1])
    assert game.game_over.get(player_id) is False

    # Clean up player state
    del game.players[player_id]
    del game.scores[player_id]
    del game.game_over[player_id]
    del game.player_names[player_id]

@pytest.mark.asyncio
async def test_wall_collision():
    """Test that hitting a wall causes game over."""
    player_id = "test_wall_collision"
    player_name = "WallTester"
    # Place player near the wall
    start_x = game.board_size[0] - 1
    start_y = game.board_size[1] // 2
    game.players[player_id] = [(start_x, start_y)]
    game.scores[player_id] = 0
    game.game_over[player_id] = False
    game.player_names[player_id] = player_name

    game.move_player(player_id, "right") # Move into the right wall

    assert game.game_over.get(player_id) is True

    # Clean up player state
    del game.players[player_id]
    del game.scores[player_id]
    del game.game_over[player_id]
    del game.player_names[player_id]