# cards.py
"""
This module defines the card and deck classes for the Mus game.
It includes card definitions, ranking, and value assignments.
"""

import random

# Define the ranks and their ordering for the Mus game.
# Note: In Mus, the ranking order (from highest to lowest) is:
# King/Three (highest), Knight, Jack, Seven, Six, Five, Four, Two/Ace (lowest).
RANKS = ['King', 'Three', 'Knight', 'Jack', 'Seven', 'Six', 'Five', 'Four', 'Two', 'Ace']

# Define ranking order values (higher numbers indicate stronger cards).
ORDER = {
    'King': 9,
    'Three': 9,  # Kings and Threes are considered equal in ranking.
    'Knight': 8,
    'Jack': 7,
    'Seven': 6,
    'Six': 5,
    'Five': 4,
    'Four': 3,
    'Two': 2,
    'Ace': 2
}

# Define point values for the cards.
VALUES = {
    'King': 10,
    'Three': 10,
    'Knight': 10,
    'Jack': 10,
    'Seven': 7,
    'Six': 6,
    'Five': 5,
    'Four': 4,
    'Two': 1,
    'Ace': 1
}

# Define suits. In Mus, the suit does not affect the ranking.
SUITS = ['Oros', 'Copas', 'Espadas', 'Bastos']

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.order = ORDER[rank]
        self.value = VALUES[rank]

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def __repr__(self):
        return self.__str__()

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS if rank in RANKS]
    
    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards):
        """Deals num_cards from the deck."""
        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt_cards
