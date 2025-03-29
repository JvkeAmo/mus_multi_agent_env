# game_logic.py
"""
This module contains the core logic for the Mus game.
It now includes:
  - Detailed betting rounds with multiple bet levels (bet, raise, call, pass, ordago).
  - Hand evaluation integration for the play categories: grande, chica, pares, and juego.
  - Turn order management and a simplified scoring and terminal state logic.
  
Note: This implementation is a simplified demonstration and can be further refined.
"""

import random
from cards import Deck
from hand_evaluation import evaluate_grande, evaluate_chica, evaluate_pairs, evaluate_juego

# game_logic.py
"""
This module contains the core logic for the Mus game, including:
  - Detailed betting rounds with nuanced actions.
  - Hand evaluation integration.
  - Special cases handling:
      - Reshuffling the discard pile when the deck runs out.
      - Refined "Órdago" (all-in) resolution with immediate hand reveal.
      - Rule exceptions regarding when hands are shown.
  - Full match logic that loops over partial games and tracks cumulative scores.
"""

import random
from cards import Deck
from hand_evaluation import evaluate_grande, evaluate_chica, evaluate_pairs, evaluate_juego

class BettingRound:
    def __init__(self, players, play_type, initial_bet=1):
        """
        Initialize a betting round.
        :param players: List of player IDs in the betting order.
        :param play_type: The play category (e.g., 'grande', 'chica', etc.).
        :param initial_bet: Starting bet value.
        """
        self.players = players
        self.play_type = play_type
        self.current_bet = initial_bet
        self.bets = {p: None for p in players}
        self.active = {p: True for p in players}  # Tracks players still in the round.
        self.last_raiser = None
        self.finished = False

    def player_action(self, player, action, amount=0):
        """
        Process an action from a player.
        :param player: Player ID.
        :param action: One of 'bet', 'raise', 'call', 'pass', or 'ordago'.
        :param amount: Amount to raise (if applicable).
        """
        if not self.active[player]:
            return

        if action == 'bet':
            # Start the betting if no bet has been made.
            if self.current_bet == 0:
                self.current_bet = 1
            self.bets[player] = self.current_bet
            self.last_raiser = player
        elif action == 'raise':
            # Increase the current bet.
            self.current_bet += amount
            self.bets[player] = self.current_bet
            self.last_raiser = player
        elif action == 'call':
            # Accept the current bet.
            self.bets[player] = self.current_bet
        elif action == 'pass':
            # Player declines further betting.
            self.active[player] = False
        elif action == 'ordago':
            # Player calls an all-in bet.
            self.bets[player] = 'ordago'
            self.finished = True

    def is_round_complete(self):
        """
        Determine if the betting round is complete.
        For simplicity, we consider it complete if:
          - Only one active player remains, or
          - All active players have bet the same amount (and no further raises).
        """
        active_players = [p for p, is_active in self.active.items() if is_active]
        if len(active_players) <= 1:
            return True
        active_bets = [self.bets[p] for p in active_players if self.bets[p] is not None and self.bets[p] != 'ordago']
        if active_bets and len(set(active_bets)) == 1:
            return True
        return False

    def get_winner(self):
        """
        Determine the winner of the betting round.
        If any player called 'ordago', return that player.
        Otherwise, the player with the highest bet wins.
        """
        for p, bet in self.bets.items():
            if bet == 'ordago':
                return p, 'ordago'
        valid_bets = {p: bet for p, bet in self.bets.items() if bet is not None}
        if valid_bets:
            winner = max(valid_bets, key=valid_bets.get)
            return winner, self.current_bet
        return None, None


class MusGame:
    def __init__(self, num_players=4, target_score=40, signal_intercept_chance=0.2):
        self.num_players = num_players
        self.target_score = target_score  # e.g., 40 stones for a complete game.
        self.deck = Deck()
        self.deck.shuffle()
        self.hands = {player: [] for player in range(num_players)}
        self.discard_pile = []
        self.current_phase = 'deal'  # Possible phases: 'deal', 'mus', 'play', 'scoring'
        self.scores = {0: 0, 1: 0}  # For two teams: team0 and team1.
        self.mano = None  # The designated "mano" (lead) player.
        self.turn_order = []  # Order of play starting with mano.
        self.current_turn_index = 0
        self.play_categories = []  # e.g., ['grande', 'chica', 'pares', 'juego']
        self.play_results = {}  # Will store (winner, final_bet) for each category.
        self.ordago_active = False
        self.ordago_player = None
        # Store the most recent covert signal for each player
        self.covert_signals = {player: 0 for player in range(num_players)}
        # Store which signals have been intercepted
        self.intercepted_signals = {player: set() for player in range(num_players)}
        # Chance that a signal will be intercepted by opponents
        self.signal_intercept_chance = signal_intercept_chance

    def draw_from_deck(self, n):
        """
        Draw n cards from the deck.
        If there are not enough cards, reshuffle the discard pile into the deck.
        """
        if len(self.deck.cards) < n:
            # Reshuffle the discard pile into the deck
            self.deck.cards.extend(self.discard_pile)
            random.shuffle(self.deck.cards)
            self.discard_pile = []
        return self.deck.deal(n)

    def initial_deal(self):
        """
        Deal 4 cards to each player, determine mano, and transition to the discard ('mus') phase.
        """
        for player in range(self.num_players):
            self.hands[player] = self.draw_from_deck(4)
        self.determine_mano()
        self.set_turn_order()
        self.current_phase = 'mus'
        self.hands_revealed = False

    def determine_mano(self):
        """
        Determine the mano (lead) by having each player reveal one card.
        The highest ranked card (based on order) wins.
        """
        drawn_cards = {}
        for player in range(self.num_players):
            # For simplicity, use the first card of each hand.
            drawn_cards[player] = self.hands[player][0]
        highest = -1
        mano_player = None
        for player, card in drawn_cards.items():
            if card.order > highest:
                highest = card.order
                mano_player = player
        self.mano = mano_player

    def set_turn_order(self):
        """
        Set the turn order for the round.
        For 4 players, assume clockwise order starting from mano.
        """
        self.turn_order = [(self.mano + i) % self.num_players for i in range(self.num_players)]
        self.current_turn_index = 0

    def current_player(self):
        """Return the ID of the current player whose turn it is."""
        return self.turn_order[self.current_turn_index]

    def advance_turn(self):
        """Advance to the next player's turn in the current turn order."""
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

    def perform_discard(self, player, cards_to_discard):
        """
        Process a discard action: remove the indicated cards from the player's hand,
        draw replacements from the deck, and add discarded cards to the discard pile.
        """
        new_hand = []
        discarded = []
        for idx, card in enumerate(self.hands[player]):
            if idx in cards_to_discard:
                discarded.append(card)
            else:
                new_hand.append(card)
        self.hands[player] = new_hand
        new_cards = self.draw_from_deck(len(discarded))
        self.hands[player].extend(new_cards)
        self.discard_pile.extend(discarded)

    def update_covert_signal(self, player, signal):
        """
        Update the covert signal for a given player.
        There's a chance that opponents might intercept the signal.
        
        :param player: The player sending the signal
        :param signal: The signal value (0-3)
        :return: A list of players who intercepted the signal (if any)
        """
        if signal == 0:  # No signal
            self.covert_signals[player] = 0
            return []
            
        # Update the player's signal
        self.covert_signals[player] = signal
        
        # Determine the player's team
        team0 = {self.mano, (self.mano + 2) % self.num_players}
        player_team = 0 if player in team0 else 1
        
        # Determine opponents (players on the other team)
        opponents = list(set(range(self.num_players)) - team0) if player_team == 0 else list(team0)
        
        # Check if opponents intercept the signal
        interceptors = []
        for opponent in opponents:
            if random.random() < self.signal_intercept_chance:
                self.intercepted_signals[opponent].add(player)
                interceptors.append(opponent)
                
        return interceptors

    def get_covert_signal(self, player):
        """
        Return the covert signal for the teammate of the given player.
        
        :param player: The player requesting the signal
        :return: The signal from their teammate
        """
        # Determine the player's team and find their teammate
        team0 = {self.mano, (self.mano + 2) % self.num_players}
        if player in team0:
            partner = self.mano if player != self.mano else (self.mano + 2) % self.num_players
        else:
            others = list(set(range(self.num_players)) - team0)
            partner = others[0] if player == others[1] else others[1]
            
        return self.covert_signals.get(partner, 0)
        
    def get_intercepted_signals(self, player):
        """
        Return signals that this player has intercepted from opponents.
        
        :param player: The player requesting intercepted signals
        :return: Dictionary mapping opponent IDs to their signals
        """
        intercepted = {}
        for opponent in self.intercepted_signals[player]:
            intercepted[opponent] = self.covert_signals[opponent]
        return intercepted

    def run_detailed_betting_round(self, play_type):
        """
        Run a detailed betting round for a given play category.
        For demonstration purposes, actions are simulated randomly.
        Returns a tuple (winner, final_bet) where final_bet is 'ordago' if an all-in is called.
        """
        betting_round = BettingRound(self.turn_order, play_type, initial_bet=1)
        while not betting_round.finished and not betting_round.is_round_complete():
            for player in self.turn_order:
                if not betting_round.active[player]:
                    continue
                # Simulate an action randomly.
                action = random.choice(['bet', 'raise', 'call', 'pass'])
                if action == 'raise':
                    amount = random.choice([1, 2])
                    betting_round.player_action(player, action, amount)
                else:
                    betting_round.player_action(player, action)
                if betting_round.is_round_complete():
                    break
            # In an actual implementation, wait for agent actions here.
        winner, final_bet = betting_round.get_winner()
        if final_bet == 'ordago':
            self.ordago_active = True
            self.ordago_player = winner
        return winner, final_bet

    def reveal_hands(self):
        """
        Reveal all players' hands.
        This method is called when a round ends or an ordago forces immediate reveal.
        """
        self.hands_revealed = True
        # In a real environment, this might log or broadcast the full hands.
        print("Revealing all hands:")
        for player in range(self.num_players):
            print(f"Player {player} hand: {self.hands[player]}")

    def resolve_ordago(self):
        """
        Resolve an ordago by revealing all hands and determining the winning team.
        For a refined resolution, we sum the card order values for each team.
        Returns the winning team index (0 or 1).
        """
        self.reveal_hands()
        team0 = {self.mano, (self.mano + 2) % self.num_players}
        team1 = set(range(self.num_players)) - team0
        score0 = sum(sum(card.order for card in self.hands[p]) for p in team0)
        score1 = sum(sum(card.order for card in self.hands[p]) for p in team1)
        if score0 > score1:
            return 0
        elif score1 > score0:
            return 1
        else:
            return None

    def start_play_phase(self):
        """
        Transition to the play phase and execute detailed betting rounds for each play category.
        After all betting rounds are complete, move to scoring.
        """
        self.current_phase = 'play'
        self.play_categories = ['grande', 'chica', 'pares', 'juego']
        self.play_results = {}
        for play in self.play_categories:
            winner, final_bet = self.run_detailed_betting_round(play)
            self.play_results[play] = (winner, final_bet)
            # If an ordago was called, break immediately.
            if self.ordago_active:
                break
        self.current_phase = 'scoring'
        self.score_round()

    def score_round(self):
        """
        Evaluate each play category using the hand evaluation functions.
        Teams (for 4 players):
          - team0: [mano, (mano+2)%4]
          - team1: remaining players.
        If an ordago is active, resolve it with immediate hand reveal.
        Otherwise, for each category, if no betting winner exists, compare hand evaluations.
        Each winning category awards 1 stone to the winning team.
        """
        team0 = {self.mano, (self.mano + 2) % self.num_players}
        team1 = set(range(self.num_players)) - team0

        round_score_team0 = 0
        round_score_team1 = 0

        # If an ordago was called, immediately resolve the round.
        if self.ordago_active:
            winning_team = self.resolve_ordago()
            if winning_team == 0:
                round_score_team0 = self.target_score  # Award full round win.
            elif winning_team == 1:
                round_score_team1 = self.target_score
        else:
            for play in self.play_categories:
                betting_winner, _ = self.play_results.get(play, (None, None))
                # Evaluate hands if no clear betting winner.
                if play == 'grande':
                    evaluations = {p: evaluate_grande(self.hands[p]) for p in range(self.num_players)}
                    best_player = max(evaluations, key=evaluations.get)
                elif play == 'chica':
                    evaluations = {p: evaluate_chica(self.hands[p]) for p in range(self.num_players)}
                    best_player = min(evaluations, key=evaluations.get)
                elif play == 'pares':
                    evaluations = {p: evaluate_pairs(self.hands[p]) for p in range(self.num_players)}
                    best_player = max(evaluations, key=evaluations.get)
                elif play == 'juego':
                    evaluations = {p: evaluate_juego(self.hands[p]) for p in range(self.num_players)}
                    best_player = max(evaluations, key=lambda p: evaluations[p])
                else:
                    best_player = None

                final_winner = betting_winner if betting_winner is not None else best_player

                if final_winner in team0:
                    round_score_team0 += 1
                elif final_winner in team1:
                    round_score_team1 += 1

        # Update overall scores for this partial game.
        self.scores[0] += round_score_team0
        self.scores[1] += round_score_team1
        # After scoring, transition back to deal for the next partial game.
        self.current_phase = 'deal'

    def is_terminal(self):
        """
        Check if either team has reached or exceeded the target score.
        """
        return self.scores[0] >= self.target_score or self.scores[1] >= self.target_score

    def get_observation(self, player):
        """
        Returns the observation for a given player.
        The observation includes:
          - A numerical representation of the player's hand (using card.order).
          - The current game phase.
          - The partner's covert signal.
          - Intercepted signals from opponents.
          - Current betting state for the active play category.
          - Scores for both teams.
        """
        # Convert the player's hand (list of card objects) to a list of numbers.
        encoded_hand = [card.order for card in self.hands[player]]
        
        # Encode the game phase as an integer
        phase_encoding = {
            'deal': 0,
            'mus': 1,
            'play': 2,
            'scoring': 3
        }
        
        # Get current betting information if in play phase
        betting_info = {}
        if self.current_phase == 'play' and hasattr(self, 'current_betting_round'):
            betting_info = {
                'current_bet': self.current_betting_round.current_bet,
                'current_category': self.play_categories.index(self.current_betting_round.play_type) 
                                   if self.current_betting_round.play_type in self.play_categories else 0
            }
        
        # Get partner's signal
        partner_signal = self.get_covert_signal(player)
        
        # Get intercepted signals from opponents
        intercepted_signals = self.get_intercepted_signals(player)
        
        observation = {
            'hand': encoded_hand,
            'phase': phase_encoding.get(self.current_phase, 0),
            'partner_signal': partner_signal,
            'intercepted_signals': intercepted_signals,
            'scores': [self.scores[0], self.scores[1]],
            'betting_info': betting_info
        }
        return observation

    def get_reward(self, player):
        """
        Returns the reward for a given player.
        Placeholder: currently returns 0 until the game is terminal.
        """
        return 0

    def start_play_phase(self):
        """
        Transition to the play phase and execute detailed betting rounds for each play category.
        After all betting rounds are complete, automatically move to scoring.
        """
        self.current_phase = 'play'
        self.play_categories = ['grande', 'chica', 'pares', 'juego']
        self.play_results = {}
        for play in self.play_categories:
            winner, final_bet = self.run_detailed_betting_round(play)
            self.play_results[play] = (winner, final_bet)
            # If an ordago was called, break immediately.
            if self.ordago_active:
                break
        self.current_phase = 'scoring'
        self.score_round()

    def finish_round(self):
        """
        Placeholder for any end-of-round cleanup or preparation for the next round.
        Currently, after scoring, the game automatically transitions back to the 'deal' phase.
        """
        self.current_phase = 'deal'

    def step(self, actions):
        """
        Process a game step based on player actions.
        Each action is expected to be a dictionary with keys:
            'action_type': integer representing the action.
                (0: discard, 1: bet, 2: raise, 3: call, 4: pass, 5: signal)
            'cards': list (binary mask) for discarding (if action_type==0).
            'amount': integer value for bet/raise actions.
            'signal': integer representing the covert signal.
        Phase transitions:
          - In the 'mus' phase, process discards and signals.
          - Then automatically transition to the play phase (which auto-handles betting rounds).
          - In the 'scoring' phase, scoring is auto-handled.
        """
        if self.current_phase == 'mus':
            # Track which players have intercepted signals
            intercepted_info = {}
            
            for player, action in actions.items():
                # Process signaling action if provided.
                if action.get('action_type') == 5 and 'signal' in action:
                    signal_value = action['signal']
                    interceptors = self.update_covert_signal(player, signal_value)
                    if interceptors:
                        intercepted_info[player] = {
                            'signal': signal_value,
                            'intercepted_by': interceptors
                        }
                
                # Process discard actions if the action type indicates discard.
                if action.get('action_type') == 0 and 'cards' in action:
                    # Convert the binary mask (e.g., [0, 1, 0, 1]) to indices.
                    cards_to_discard = [i for i, v in enumerate(action.get('cards', [])) if v == 1]
                    self.perform_discard(player, cards_to_discard)
            
            # After processing discards/signals in the mus phase, move to play.
            self.start_play_phase()
            
            # Return information about intercepted signals
            return intercepted_info
            
        elif self.current_phase == 'play':
            # For this iteration, betting rounds are auto-handled.
            # Future versions may use agent actions for betting in the play phase.
            self.start_play_phase()  # This call will run betting rounds and then scoring.
            return {}
            
        elif self.current_phase == 'scoring':
            # Scoring is auto-handled in score_round().
            # After scoring, finish the round.
            self.finish_round()
            return {}
            
        return {}

class MusMatch:
    """
    This class manages a full match of Mus, composed of multiple partial games.
    A match is won by the team that wins a predetermined number of partial games.
    """
    def __init__(self, num_players=4, target_score=40, match_games=3):
        """
        :param num_players: Number of players (typically 4 for 2v2).
        :param target_score: Score needed to win a partial game.
        :param match_games: Number of partial game wins required to win the match.
        """
        self.num_players = num_players
        self.target_score = target_score
        self.match_games = match_games
        self.match_score = {0: 0, 1: 0}
        self.current_game = None

    def play_partial_game(self):
        """
        Play a single partial game of Mus.
        For simulation purposes, we assume that all players take a default action (no discards).
        In a full implementation, actions would be provided by agents.
        """
        self.current_game = MusGame(num_players=self.num_players, target_score=self.target_score)
        self.current_game.initial_deal()
        # For simulation, assume no discards:
        actions = {p: {'type': 'discard', 'cards': []} for p in range(self.num_players)}
        self.current_game.step(actions)
        # Determine the winner of this partial game:
        team0 = {self.current_game.mano, (self.current_game.mano + 2) % self.num_players}
        if self.current_game.scores[0] > self.current_game.scores[1]:
            return 0
        elif self.current_game.scores[1] > self.current_game.scores[0]:
            return 1
        else:
            return None  # A tie; you may want to handle ties explicitly.

    def play_match(self):
        """
        Loop over partial games until one team wins the match.
        Returns the winning team and the match score.
        """
        while self.match_score[0] < self.match_games and self.match_score[1] < self.match_games:
            winner = self.play_partial_game()
            if winner is not None:
                self.match_score[winner] += 1
                print(f"Partial game winner: Team {winner}. Current match score: {self.match_score}")
            else:
                print("Partial game tied; replaying game.")
        overall_winner = 0 if self.match_score[0] >= self.match_games else 1
        print(f"Match complete. Winning team: Team {overall_winner}")
        return overall_winner, self.match_score