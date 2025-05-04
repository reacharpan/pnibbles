Database API
============

This module handles all database operations for storing and retrieving high scores.

Database Schema
--------------

.. mermaid::

   erDiagram
      high_scores {
         int id PK
         string player_name
         int score
         datetime date
      }

Flow Diagram
-----------

.. mermaid::

   graph TD
      A[Initialize DB] --> B[Create Tables]
      C[Save Score] --> D{Is Top 10?}
      D -->|Yes| E[Insert Score]
      D -->|No| F[Discard Score]
      G[Get Top Scores] --> H[Query DB]
      H --> I[Return Scores]

API Reference
------------

Database Operations
-----------------

.. autofunction:: db.init_db
   :noindex:

.. autofunction:: db.save_score
   :noindex:

.. autofunction:: db.get_top_scores
   :noindex:

Configuration
------------

The database uses SQLite and stores data in the following location:

.. code-block:: python

   DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'scores.db')