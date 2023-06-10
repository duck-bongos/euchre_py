"""A module containing the class to build a record for any database consumption.

Converts normal gameplay into MongoDB-friendly format. Also converts the gameplay
into a matrix to train a RNN."""

from typing import Any, Dict, List, Union

import numpy as np

from .utils import Score, Trump

CARD_IDXS = {
    "Nine of Clubs": 0,
    "Ten of Clubs": 1,
    "Jack of Clubs": 2,
    "Queen of Clubs": 3,
    "King of Clubs": 4,
    "Ace of Clubs": 5,
    "Nine of Diamonds": 6,
    "Ten of Diamonds": 7,
    "Jack of Diamonds": 8,
    "Queen of Diamonds": 9,
    "King of Diamonds": 10,
    "Ace of Diamonds": 11,
    "Nine of Spades": 12,
    "Ten of Spades": 13,
    "Jack of Spades": 14,
    "Queen of Spades": 15,
    "King of Spades": 16,
    "Ace of Spades": 17,
    "Nine of Hearts": 18,
    "Ten of Hearts": 19,
    "Jack of Hearts": 20,
    "Queen of Hearts": 21,
    "King of Hearts": 22,
    "Ace of Hearts": 23,
}


class Record:
    def __init__(self, gameplay: Dict[str, Any]):
        self.hr: Dict[str, Any] = gameplay.copy()  # human_readable
        self.hand_num: int = gameplay["hand_num"]
        self.players: List[Dict[str, Union[str, int]]] = gameplay["players"]
        self.trump: Trump = gameplay["trump"]
        self.trump_bidder_idx: int = gameplay["trump_bidder_idx"]
        self.trump_bidding_round: int = gameplay["round"]
        self.lead_suit: int = gameplay["lead_suit"]
        self.dealer: int = gameplay["dealer"]
        self.turn_idx: int = gameplay["turn_idx"]
        self.score: Score = gameplay["score"]
        self.current_trick: List[Dict[str, Union[str, int]]] = gameplay["current_trick"]
        self.__matrix: np.ndarray

        # initialize the matrix
        self._create_matrix()

    def _create_matrix(self):
        """Create a 55x4 matrix that represents the data from the game.

        Build a matrix that sets up all the data needed to train an RNN.
        Column IDXs:
            idx + 1 = player ID, where relevant.
            trump suit, where relevant

        Row IDXs:
            0-23: One-hot matrix of Players' hands, uses CARD_IDXs
            24-47: Current trick, uses CARD_IDXs + 24
            48: trump suit - 0: Clubs, 1: Diamonds, 2: Spades, 3: Hearts
            49: trump bidder ID
            50: Alone: 1 for whomever called alone
            51: round - only first element, m[51,0] what round of bidding did this occur? 3 = "screw the dealer"
            52: dealer idx
            53: turn idx - whose turn it is
            54: lead suit - 0: Clubs, 1: Diamonds, 2: Spades, 3: Hearts
            55: tricks won
            56: team points
        """
        m = np.zeros((57, 4))

        # set player info
        for player in self.players:
            idx = player["id"]
            # tricks won
            m[55, idx] = player["tricks_won"]
            for card in player["hand"]:
                c = str(card)
                c_idx = CARD_IDXS[c]
                m[c_idx, idx] = 1

        # set current trick
        for play in self.current_trick:
            idx = play["player_id"] - 1
            c = str(play["card"])

            c_idx = CARD_IDXS[c]
            m[c_idx + 24, idx] = 1

        # set trump & alone
        m[48, self.trump.suit] = 1
        m[49, self.trump_bidder_idx] = 1
        if self.trump.alone == 1:
            m[50, self.trump_bidder_idx] = 1

        # what round
        m[51, 0] = self.trump_bidding_round

        # set dealer
        m[52, self.dealer] = 1

        # turn
        m[53, self.turn_idx] = 1

        # lead suit
        m[54, self.lead_suit] = 1

        # team points
        m[56, 0] = self.score.evens
        m[56, 2] = self.score.evens

        m[56, 1] = self.score.odds
        m[56, 3] = self.score.odds

        self.set_matrix(m)

    def set_matrix(self, matrix: np.ndarray):
        self.__matrix = matrix.copy()

    def matrix(self):
        return self.__matrix

    def data(self):
        return list([list(row) for row in self.__matrix])

    def __call__(self):
        for p in self.players:
            p["hand"] = [str(c) for c in p["hand"]]
        self.hr["trump"] = str(self.trump)
        self.hr["score"] = str(self.score)
        self.hr["data"] = self.data()

        return self.hr
