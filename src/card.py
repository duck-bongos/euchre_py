"""Card class"""

VALUES = {
    0: "NULL",
    9: "Nine",
    10: "Ten",
    11: "Jack",
    12: "Queen",
    13: "King",
    14: "Ace",
}

SUITS = {-1: "NULL", 0: "Clubs", 1: "Diamonds", 2: "Spades", 3: "Hearts"}


class Card:
    def __init__(self, value: int = 0, suit: int = -1):
        self.value = 0 or value
        self.suit = -1 if suit < 0 else suit
        # 0 if black, 1 if red
        self.color = -1 if suit < 0 else suit % 2

    def set_trump(self, trump_suit: int):
        ts = trump_suit % 2
        # right bauer
        if self.value == 11 and self.suit == trump_suit:
            self.value = 25

        # left bauer
        elif self.value == 11 and self.color == ts:
            self.value = 24

        # everything else
        elif trump_suit == self.suit:
            self.value += 9

    def unset_trump(self):
        if self.value >= 24:
            self.value = 11

        elif self.value >= 18 and self.value < 24:
            self.value -= 9

    def __repr__(self):
        return f"{VALUES[self.value]} of {SUITS[self.suit]}"

    def __str__(self) -> str:
        return self.__repr__()
