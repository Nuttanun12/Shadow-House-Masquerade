import sqlite3
import os
import json

class DatabaseManager:
    def __init__(self, db_path="game_records.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise

    def _init_db(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Table for player statistics
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS player_stats (
                        player_name TEXT PRIMARY KEY,
                        games_played INTEGER DEFAULT 0,
                        wins INTEGER DEFAULT 0,
                        total_score INTEGER DEFAULT 0
                    )
                ''')
                # Table for game history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS game_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        winner_name TEXT,
                        final_scores TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")

    def update_player_stats(self, name, won, score):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO player_stats (player_name, games_played, wins, total_score)
                    VALUES (?, 1, ?, ?)
                    ON CONFLICT(player_name) DO UPDATE SET
                        games_played = games_played + 1,
                        wins = wins + ?,
                        total_score = total_score + ?
                ''', (name, 1 if won else 0, score, 1 if won else 0, score))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating player stats: {e}")

    def record_game(self, winner_name, final_scores_dict):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO game_history (winner_name, final_scores)
                    VALUES (?, ?)
                ''', (winner_name, json.dumps(final_scores_dict)))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error recording game: {e}")

    def get_leaderboard(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM player_stats ORDER BY wins DESC, total_score DESC')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching leaderboard: {e}")
            return []

    def get_history(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM game_history ORDER BY date_played DESC LIMIT 10')
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching history: {e}")
            return []
