Mus RL Environment
===================

Description
-----------
This repository provides a multi-agent reinforcement learning (RL) environment for the traditional Spanish card game "Mus." Mus is a unique 2v2 card game where teammates must cooperate while competing against an opposing duo. Its blend of hidden information, strategic discarding, betting rounds, and even covert communication makes it an ideal testbed for multi-agent RL research in mixed cooperative-adversarial settings.

Game Rules Overview
-------------------
Objective:
- Win the match by reaching a target score (commonly 8 scoring units, equivalent to 40 stones) over one or several rounds.

Deck and Card Values:
- **Deck:** Uses a 40-card Spanish deck.
- **Card Ranking (highest to lowest):** King/Three, Knight, Jack, Seven, Six, Five, Four, Two/Ace.
- **Card Points:** Kings, Threes, Knights, and Jacks are worth 10 points; other cards retain their numeric values, except Twos (and Aces) which count as 1 point.

Players and Teams:
- Typically played with four players in two partnerships.
- An initial card draw determines seating and roles. The highest card becomes the “lead” (mano), with their partner seated opposite.

Game Flow:
1. **Discard Phase ("Mus"):**
   - After dealing four cards to each player, everyone examines their hand and decides whether to discard (by declaring “Mus”) to improve their hand.
   - If all agree, each player may exchange any number of cards. This process can be repeated until any player calls “No Mus,” which finalizes the hands.
2. **Play Phase (Betting and Revealing Hands):**
   - The game proceeds through several betting rounds, each focused on a different aspect:
     - **Grande:** Compete for the best high cards.
     - **Chica:** Compete for the best low cards.
     - **Pairs:** Form pairs, three-of-a-kind, or two pairs.
     - **Juego (Point):** Based on the sum of the card values. A hand qualifies as having “Juego” if its total is 31 or more, with 31 being the best. If no hand reaches 31, the best “point” (with 30 as the highest) wins.
   - Players take turns to bet, raise, or pass, with points (or stones) being awarded immediately for wins or penalties.
3. **Scoring:**
   - At the end of each round, all players reveal their hands to verify wins in each category. Points are recorded using stones or markers.
   - The match continues until one team reaches the target score.

Multi-Agent RL Environment Purpose
------------------------------------
This project aims to create a robust environment for developing and testing multi-agent RL algorithms in a setting that requires both teamwork and competition:
- **Team Coordination:** Agents on the same team must learn to cooperate, potentially through implicit signals, to optimize joint performance.
- **Adversarial Strategy:** Agents must also adapt to the competitive strategies of the opposing team, handling hidden information and uncertainty.
- **Research and Experimentation:** The complexity of Mus—its discarding phase, strategic betting, and hidden hands—provides a rich domain for exploring novel multi-agent learning approaches and emergent behaviors.

Repository Structure and Getting Started
------------------------------------------
- **Source Code:** Contains the implementation of the Mus game mechanics and multi-agent interface.
- **Documentation:** Provides further details on game rules, environment API, and integration with popular RL frameworks.
- **Examples:** Includes sample scripts demonstrating how to train agents using frameworks like PettingZoo, RLlib, or OpenSpiel.

Installation and Usage:
1. Clone the repository.
2. Install the necessary dependencies (see requirements.txt).
3. Run the provided example scripts to begin training or testing your agents.

Contributions and Future Work:
- Contributions are welcome! We encourage improvements in game mechanics, feature enhancements, and integration of additional RL algorithms.
- Future updates may include more nuanced communication signals, refined scoring mechanisms, and support for additional game variants.

License
-------
This project is licensed under the [Your License Here] license.

Contact
-------
For questions, suggestions, or further discussions, please open an issue or contact the repository maintainer.

Enjoy exploring the strategic depths of Mus and advancing multi-agent reinforcement learning research!
