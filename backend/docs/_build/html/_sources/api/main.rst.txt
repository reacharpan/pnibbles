Main Game API
============

This module implements the main game logic and FastAPI endpoints for the Snake game.

WebSocket Game Loop
------------------

.. mermaid::

   sequenceDiagram
      participant C as Client
      participant S as Server
      participant G as Game State
      participant D as Database
      
      C->>S: Connect to WebSocket
      C->>S: Send Player Name
      S->>G: Initialize Player
      S-->>C: Send Initial Game State
      loop Game Loop
         C->>S: Send Direction
         S->>G: Update Game State
         G->>G: Check Collisions
         G->>G: Update Score
         alt Game Over
            G->>D: Save Score
            S-->>C: Send Game Over + High Scores
         else Game Continues
            S-->>C: Send Updated Game State
         end
      end

API Reference
------------

FastAPI Application
-----------------

.. autofunction:: main.app
   :noindex:

Game State Management
-------------------

.. autoclass:: main.SnakeGame
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

API Endpoints
------------

Root Endpoint
------------

.. autofunction:: main.get
   :noindex:

High Scores Endpoint
------------------

.. autofunction:: main.get_high_scores
   :noindex:

WebSocket Endpoint
----------------