"""Card class"""
from typing import Dict

VALUES = {
    0: "NULL",
    9: "Nine",
    10: "Ten",
    11: "Jack",
    12: "Queen",
    13: "King",
    14: "Ace",
    18: "Nine",
    19: "Ten",
    20: "Jack",
    21: "Queen",
    22: "King",
    23: "Ace",
    24: "Jack",
    25: "Jack",
}

SUITS = {-1: "NULL", 0: "Clubs", 1: "Diamonds", 2: "Spades", 3: "Hearts"}


class Card:
    def __init__(self, value: int = 0, suit: int = -1):
        self.value = 0 or value
        self.suit = -1 if suit < 0 else suit
        # 0 if black, 1 if red
        self.color = -1 if suit < 0 else suit % 2
        self.bauer = -1  # 0 if left, 1 if right

    def set_trump(self, trump_suit: int):
        ts = trump_suit % 2
        # right bauer
        if self.value == 11 and self.suit == trump_suit and self.bauer != 0:
            self.value = 25
            self.bauer = 1

        # left bauer
        elif self.value == 11 and self.color == ts and self.bauer == -1:
            self.value = 24
            self.bauer = 0
            pass

        # everything else
        elif trump_suit == self.suit:
            if self.value > 14:
                print()
                pass
            self.value += 9

        if self.value > 25:
            print("uh oh")
            pass

    def unset_trump(self):
        if self.value >= 24:
            self.value = 11

        elif self.value >= 18 and self.value < 24:
            self.value -= 9

        self.bauer = -1

    def __repr__(self):
        r = f"{VALUES[self.value]} of {SUITS[self.suit]}"
        return r

    def __str__(self) -> str:
        return self.__repr__()

    def __call__(self) -> Dict[str, int]:
        return {"suit": self.suit, "value": self.value}
