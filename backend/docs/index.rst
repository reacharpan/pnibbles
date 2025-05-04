Welcome to pnibbles documentation!
=================================

Pnibbles is a multiplayer snake game with a Python FastAPI backend and a web frontend.

.. mermaid::

   graph TD
      A[Client Connect] --> B[WebSocket Connection]
      B --> C{Game Loop}
      C --> D[Handle Player Move]
      C --> E[Check Collisions]
      C --> F[Update Score]
      E --> G{Game Over?}
      G -->|Yes| H[Save Score]
      G -->|No| C
      F --> C

Architecture Overview
---------------------

.. mermaid::

   graph LR
      A[Frontend] -->|WebSocket| B[FastAPI Backend]
      B -->|Game State| A
      B --> C[(SQLite DB)]
      C -->|High Scores| B

API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/main
   api/db
   
Game Components
---------------

Main Game Logic
^^^^^^^^^^^^^^^

.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:

Database Operations
^^^^^^^^^^^^^^^^^^^

.. automodule:: db
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

