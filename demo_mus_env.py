#!/usr/bin/env python3
"""
demo_mus_env.py

A script to demonstrate the Mus environment with random agents.
This shows how the environment can be used for reinforcement learning,
with a focus on the signaling mechanism.
"""

from mus_env import MusEnv
import numpy as np
import time

def main():
    # Create the environment with a 20% chance of signal interception
    env = MusEnv(num_players=4, signal_intercept_chance=0.2)
    
    # Run several episodes
    for episode in range(3):
        print(f"\n\nEPISODE {episode+1}")
        print("="*50)
        
        # Reset the environment
        observations = env.reset()
        
        # Print initial state
        env.render()
        
        done = {'__all__': False}
        step_count = 0
        
        # Run until episode is done
        while not done['__all__'] and step_count < 20:  # Limit steps to avoid infinite loops
            print(f"\nStep {step_count+1}")
            
            # Generate random actions for each player
            actions = {}
            for player in range(env.num_players):
                # Create appropriate actions based on the game phase
                if env.game.current_phase == 'mus':
                    # In mus phase, randomly decide to discard or signal
                    if np.random.random() < 0.5:  # 50% chance to discard
                        actions[player] = {
                            'action_type': 0,  # Discard
                            'cards': np.random.randint(0, 2, size=4).tolist()  # Random discard pattern
                        }
                    else:
                        # Increase probability of signaling to demonstrate the feature
                        actions[player] = {
                            'action_type': 5,  # Signal
                            'signal': np.random.randint(1, 4)  # Random signal 1-3
                        }
                elif env.game.current_phase == 'play':
                    # In play phase, randomly choose a betting action
                    action_type = np.random.choice([1, 2, 3, 4])  # bet, raise, call, pass
                    actions[player] = {
                        'action_type': action_type,
                        'amount': np.random.randint(1, 4) if action_type in [1, 2] else 0
                    }
                else:
                    # Default action for other phases
                    actions[player] = {'action_type': 0}
            
            # Take a step in the environment
            observations, rewards, done, info = env.step(actions)
            
            # Print the actions taken
            print("Actions taken:")
            for player, action in actions.items():
                action_names = {0: "Discard", 1: "Bet", 2: "Raise", 3: "Call", 4: "Pass", 5: "Signal"}
                action_type = action.get('action_type', 0)
                action_name = action_names.get(action_type, "Unknown")
                
                if action_type == 0 and 'cards' in action:  # Discard
                    print(f"Player {player}: {action_name} cards {action['cards']}")
                elif action_type == 5:  # Signal
                    print(f"Player {player}: {action_name} {action.get('signal', 0)}")
                elif action_type in [1, 2]:  # Bet or Raise
                    print(f"Player {player}: {action_name} amount {action.get('amount', 0)}")
                else:
                    print(f"Player {player}: {action_name}")
            
            # Render the environment
            env.render()
            
            # Print rewards
            print("Rewards:")
            for player, reward in rewards.items():
                print(f"Player {player}: {reward}")
            
            # Print intercepted signals information
            if hasattr(env.game, 'step') and callable(env.game.step):
                intercepted_info = env.game.step({})  # Get information about intercepted signals
                if intercepted_info:
                    print("\nIntercepted Signals:")
                    for sender, info in intercepted_info.items():
                        print(f"Player {sender}'s signal {info['signal']} was intercepted by players {info['intercepted_by']}")
            
            step_count += 1
            time.sleep(1)  # Slow down for readability
        
        print(f"\nEpisode {episode+1} complete after {step_count} steps")
        if done['__all__']:
            print("Game reached terminal state")
            # Print final scores
            print(f"Final scores - Team 0: {env.game.scores[0]}, Team 1: {env.game.scores[1]}")
            winner = 0 if env.game.scores[0] > env.game.scores[1] else 1
            print(f"Winner: Team {winner}")

if __name__ == "__main__":
    main() 