# hand_evaluation.py
"""
This module provides hand evaluation functions for the Mus game for each play category:
- Grande: Best high cards.
- Chica: Best low cards.
- Pares: Pairs evaluation (single pair, three-of-a-kind, or two pairs).
- Juego: Sum of card values evaluation.
"""

def evaluate_grande(hand):
    """
    Evaluate hand for 'Grande' category.
    Returns a tuple of card orders sorted in descending order.
    A higher tuple (lexicographically) indicates a stronger hand.
    """
    sorted_orders = sorted([card.order for card in hand], reverse=True)
    return tuple(sorted_orders)

def evaluate_chica(hand):
    """
    Evaluate hand for 'Chica' category.
    Returns a tuple of card orders sorted in ascending order.
    A lower tuple (lexicographically) indicates a stronger hand.
    """
    sorted_orders = sorted([card.order for card in hand])
    return tuple(sorted_orders)

def evaluate_pairs(hand):
    """
    Evaluate hand for 'Pares' category.
    Returns a tuple where the first element indicates the category:
      0 - No pair
      1 - Single pair
      2 - Three-of-a-kind (Medias)
      3 - Two pairs (Duples)
    Followed by one or more tie-breaker values (the ORDER values of the relevant rank(s)).
    """
    from collections import Counter
    counts = Counter(card.rank for card in hand)
    pairs = [rank for rank, count in counts.items() if count == 2]
    triples = [rank for rank, count in counts.items() if count == 3]
    quads = [rank for rank, count in counts.items() if count == 4]
    
    # Import the ranking order dictionary from cards.py
    try:
        from cards import ORDER
    except ImportError:
        ORDER = {}

    if quads:
        # Four-of-a-kind: for simplicity, treat as two pairs (Duples).
        return (3, ORDER.get(quads[0], 0))
    elif triples:
        return (2, ORDER.get(triples[0], 0))
    elif len(pairs) == 2:
        sorted_pairs = sorted([ORDER.get(rank, 0) for rank in pairs], reverse=True)
        return (3,) + tuple(sorted_pairs)
    elif len(pairs) == 1:
        return (1, ORDER.get(pairs[0], 0))
    else:
        return (0,)

def evaluate_juego(hand):
    """
    Evaluate hand for 'Juego' category.
    Sums the card values. If the total is 31 or more, the hand qualifies as 'juego' and
    is ranked according to Mus rules:
      31 is best, then 32, then 40, followed by 37, 36, 35, 34, and 33.
    If the total is less than 31, the hand is ranked solely by its point sum.
    Returns a tuple (is_juego, rank) where is_juego is 1 if the hand qualifies as juego, 0 otherwise.
    """
    total = sum(card.value for card in hand)
    juego_ranking = {
        31: 8,
        32: 7,
        40: 6,
        37: 5,
        36: 4,
        35: 3,
        34: 2,
        33: 1
    }
    if total >= 31:
        rank = juego_ranking.get(total, 0)
        return (1, rank)
    else:
        return (0, total)
