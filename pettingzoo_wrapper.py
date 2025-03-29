# pettingzoo_wrapper.py
"""
This module wraps the MusEnv (our Gym-based multi-agent environment for Mus)
into a PettingZoo-compatible ParallelEnv.
"""

from pettingzoo import ParallelEnv
from pettingzoo.utils import wrappers
import numpy as np
from mus_env import MusEnv

class PettingZooMusEnv(ParallelEnv):
    metadata = {"render.modes": ["human"]}
    
    def __init__(self, num_players=4):
        super().__init__()
        self.num_players = num_players
        # Define agent names
        self.agents = [f"player_{i}" for i in range(num_players)]
        self.possible_agents = self.agents[:]
        # Create an instance of our MusEnv
        self.env = MusEnv(num_players=num_players)
        # Use the observation and action spaces from our Gym environment.
        self.observation_space = self.env.observation_space
        self.action_space = self.env.action_space

    def reset(self, seed=None, options=None):
        """
        Reset the environment and return observations for all agents.
        """
        obs = self.env.reset()
        observations = {f"player_{i}": obs[i] for i in range(self.num_players)}
        return observations

    def step(self, actions):
        """
        Accept a dictionary of actions keyed by agent names,
        convert them into our internal representation (indexed by player id),
        and perform a step in the MusEnv.
        Returns observations, rewards, dones, and infos as dictionaries keyed by agent names.
        """
        # Convert actions: keys are "player_i", map them to indices.
        action_dict = {i: actions[f"player_{i}"] for i in range(self.num_players)}
        obs, rewards, dones, infos = self.env.step(action_dict)
        observations = {f"player_{i}": obs[i] for i in range(self.num_players)}
        rewards = {f"player_{i}": rewards[i] for i in range(self.num_players)}
        dones = {f"player_{i}": dones[i] for i in range(self.num_players)}
        dones["__all__"] = dones["__all__"]
        infos = {f"player_{i}": infos[i] for i in range(self.num_players)}
        return observations, rewards, dones, infos

    def render(self, mode="human"):
        """
        Render the underlying MusEnv.
        """
        self.env.render(mode)

if __name__ == "__main__":
    # Simple test script to run the environment.
    env = PettingZooMusEnv(num_players=4)
    observations = env.reset()
    print("Initial Observations:")
    for agent, obs in observations.items():
        print(f"{agent}: {obs}")
    
    done = {"__all__": False}
    step_count = 0
    while not done["__all__"] and step_count < 5:
        # For testing, sample random actions for each agent.
        actions = {agent: env.action_space.sample() for agent in env.agents}
        observations, rewards, done, infos = env.step(actions)
        print(f"\nStep {step_count+1}:")
        for agent in env.agents:
            print(f"{agent} observation: {observations[agent]}, reward: {rewards[agent]}")
        step_count += 1
        env.render()
