from typing import Any, Dict
from .card import SUITS


class Score:
    def __init__(self, odds: int = 0, evens: int = 0) -> None:
        self.odds = odds
        self.evens = evens

    def __repr__(self) -> str:
        return f"Odds: {self.odds} Evens: {self.evens}"

    def __str__(self) -> str:
        return self.__repr__()

    def __call__(self) -> Dict[str, int]:
        return {
            "odds": self.odds,
            "evens": self.evens,
        }


class HandScore:
    def __init__(self, score: int, prob: float = 0.0) -> None:
        self.score = score
        self.prob = prob

    def __repr__(self) -> str:
        return f"Score: {self.score} Probability: {self.prob}"

    def __str__(self) -> str:
        return self.__repr__()

    def __call__(self) -> Dict[str, int]:
        return {
            "score": self.score,
            "probability": self.prob,
        }


class Trump:
    def __init__(self, suit: int = -1, alone: int = 0) -> None:
        self.suit = suit
        self.alone = alone

    def __repr__(self) -> str:
        alone = "Alone" if self.alone else ""
        return f"{SUITS[self.suit]} {alone}"

    def __str__(self) -> str:
        return self.__repr__()

    def __call__(self) -> Any:
        return {"suit": self.suit, "alone": self.alone}


class BestCard:
    def __init__(self, card=None, idx=-1) -> None:
        self.card = card
        self.idx = idx

    def __repr__(self) -> str:
        return f"Card: {repr(self.card)} Index: {self.idx}"

    def __str__(self) -> str:
        return self.__repr__()
