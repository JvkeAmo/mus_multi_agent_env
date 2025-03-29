# mus_env.py
"""
This module implements the multi-agent RL environment for the Mus game.
It provides the Gym interface (reset, step, render) so that it can be used with RL libraries.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from game_logic import MusGame

class MusEnv(gym.Env):
    """
    Custom multi-agent environment for the Mus card game.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, num_players=4):
        super(MusEnv, self).__init__()
        self.num_players = num_players
        self.game = MusGame(num_players=num_players)
        
        # Define a richer action space.
        # action_type: 0: discard, 1: bet, 2: raise, 3: call, 4: pass, 5: signal.
        # cards: a binary vector for each of the 4 cards (only relevant for discard).
        # amount: integer value for bet/raise (if applicable).
        # signal: discrete value for signaling (e.g., 0-3).
        self.action_space = spaces.Dict({
            'action_type': spaces.Discrete(6),
            'cards': spaces.MultiBinary(4),
            'amount': spaces.Box(low=0, high=10, shape=(), dtype=np.int32),
            'signal': spaces.Discrete(4)
        })
        
        # Define an observation space.
        # Here, 'hand' is a numerical representation (list of 4 card orders).
        self.observation_space = spaces.Dict({
            'hand': spaces.Box(low=0, high=10, shape=(4,), dtype=np.int32),
            'phase': spaces.Discrete(4),  # 0: deal, 1: mus, 2: play, 3: scoring.
            'covert_signal': spaces.Discrete(4),
            'scores': spaces.Box(low=0, high=40, shape=(2,), dtype=np.int32),
            'betting_info': spaces.Dict({
                'current_bet': spaces.Box(low=0, high=40, shape=(), dtype=np.int32),
                'current_category': spaces.Discrete(4)  # 0: grande, 1: chica, 2: pares, 3: juego
            })
        })

        self.reset()

    def reset(self):
        """
        Resets the environment for a new game round.
        Returns:
            A dictionary of observations for each agent.
        """
        self.game = MusGame(num_players=self.num_players)
        self.game.initial_deal()
        observations = {player: self.game.get_observation(player) for player in range(self.num_players)}
        return observations
    
    def get_observation(self, player):
        """
        Returns the observation for the given player.
        In addition to their hand and the current phase, this observation
        includes a 'covert_signal' field.
        """
        observation = {
            'hand': self.game.hands[player],  # Your hand representation.
            'phase': self.game.current_phase,
            # 'covert_signal' might be the last signal from the teammate.
            'covert_signal': self.game.get_covert_signal(player)
        }
        return observation


    def step(self, actions):
        """
        Executes a step in the environment given actions from each agent.
        Parameters:
            actions (dict): Mapping from player IDs to their action dictionaries.
        Returns:
            observations, rewards, done, info (all dictionaries keyed by player ID).
        """
        # Process actions based on the current game phase
        processed_actions = {}
        
        for player, action in actions.items():
            processed_action = {}
            action_type = action.get('action_type', 0)
            
            if self.game.current_phase == 'mus':
                if action_type == 0:  # Discard
                    processed_action['action_type'] = 0
                    processed_action['cards'] = action.get('cards', [0, 0, 0, 0])
                elif action_type == 5:  # Signal
                    processed_action['action_type'] = 5
                    processed_action['signal'] = action.get('signal', 0)
            
            elif self.game.current_phase == 'play':
                if action_type in [1, 2, 3, 4]:  # Betting actions
                    processed_action['action_type'] = action_type
                    if action_type in [1, 2]:  # Bet or raise
                        processed_action['amount'] = action.get('amount', 1)
            
            processed_actions[player] = processed_action
        
        self.game.step(processed_actions)

        observations = {}
        rewards = {}
        done = {}
        info = {}

        for player in range(self.num_players):
            observations[player] = self.game.get_observation(player)
            rewards[player] = self.game.get_reward(player)
            done[player] = self.game.is_terminal()
            info[player] = {}  # Additional info can be provided here.

        done['__all__'] = all(done[player] for player in range(self.num_players))
        return observations, rewards, done, info

    def render(self, mode='human'):
        """
        Renders the current game state.
        """
        print("\n" + "="*50)
        print(f"GAME STATE - Phase: {self.game.current_phase}")
        print(f"Scores - Team 0: {self.game.scores[0]}, Team 1: {self.game.scores[1]}")
        
        # Show the current player's turn
        if hasattr(self.game, 'current_turn_index') and self.game.turn_order:
            current_player = self.game.current_player()
            print(f"Current Player: {current_player}")
        
        # Show betting information if in play phase
        if self.game.current_phase == 'play':
            if hasattr(self.game, 'current_betting_round'):
                print(f"Current Play Category: {self.game.current_betting_round.play_type}")
                print(f"Current Bet: {self.game.current_betting_round.current_bet}")
        
        # Show each player's hand
        for player in range(self.num_players):
            team = "Team 0" if player in [self.game.mano, (self.game.mano + 2) % self.num_players] else "Team 1"
            hand_str = ", ".join([f"{card.rank} of {card.suit}" for card in self.game.hands[player]])
            print(f"Player {player} ({team}) Hand: {hand_str}")
            
            # Show signals if any
            if self.game.covert_signals[player] > 0:
                print(f"  Signal: {self.game.covert_signals[player]}")
        
        print("="*50)
