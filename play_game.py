#!/usr/bin/env python3
"""
play_game.py

A standalone script to play a full match of Mus using the current game logic.
This script uses the MusMatch class to simulate a match.
The other three players use default actions.
The game state is printed to the console at key points.
"""

from game_logic import MusMatch
import time

def main():
    print("Starting a full match of Mus!")
    # Create a match: 4 players, target_score of 40 for a partial game,
    # and a match is won by winning 3 partial games.
    match = MusMatch(num_players=4, target_score=40, match_games=3)
    
    # Play the match; the play_match() method prints partial game results.
    overall_winner, final_score = match.play_match()
    
    print(f"\nMatch complete. Winning Team: Team {overall_winner}")
    print("Final match score:", final_score)

if __name__ == "__main__":
    main()
