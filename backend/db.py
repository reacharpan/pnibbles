import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'scores.db')

def init_db():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create scores table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS high_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT NOT NULL,
        score INTEGER NOT NULL,
        date TIMESTAMP NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def save_score(player_name: str, score: int) -> bool:
    """Save a score and return True if it made it to top 10"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the current lowest score in top 10
    cursor.execute('SELECT MIN(score) FROM high_scores WHERE id IN (SELECT id FROM high_scores ORDER BY score DESC LIMIT 10)')
    lowest_score = cursor.fetchone()[0]
    
    is_top_10 = False
    if lowest_score is None or score > lowest_score or cursor.execute('SELECT COUNT(*) FROM high_scores').fetchone()[0] < 10:
        # Add the new score
        cursor.execute('INSERT INTO high_scores (player_name, score, date) VALUES (?, ?, ?)',
                      (player_name, score, datetime.now().isoformat()))
        is_top_10 = True
    
    conn.commit()
    conn.close()
    return is_top_10

def get_top_scores(limit: int = 10):
    """Get the top scores"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT player_name, score, date FROM high_scores ORDER BY score DESC LIMIT ?', (limit,))
    scores = cursor.fetchall()
    
    conn.close()
    return [{'player_name': name, 'score': score, 'date': date} for name, score, date in scores]