from math import log1p
from random import randrange
from typing import List, Tuple

from .card import Card
from .utils import BestCard, HandScore, Score, Trump

LONER_PROBABILITY = 3.5

FOLLOW_PROBS = {
    25: 1.0,  # left bauer
    24: 23 / 24,  # right bauer
    23: 22 / 24,
    22: 21 / 24,
    21: 20 / 24,
    20: 19 / 24,
    19: 18 / 24,
    18: 17 / 24,  # 9 of trump
    14: 5 / 24,
    13: 1 / 6,
    12: 1 / 8,
    11: 1 / 12,
    10: 1 / 24,
    9: 0.0,
}

LEAD_PROBABILITIES = {
    25: 1.0,  # left bauer
    24: 23 / 24,  # right bauer
    23: 22 / 24,
    22: 21 / 24,
    21: 20 / 24,
    20: 19 / 24,
    19: 18 / 24,
    18: 17 / 24,  # 9 of trump
    14: 16 / 24,
    13: 15 / 24,
    12: 14 / 24,
    11: 13 / 24,
    10: 12 / 24,
    9: 11 / 24,
}


class Player:
    def __init__(self) -> None:
        self.team = 0
        self.name = "Player Zero"
        self.hand: List[Card] = []
        self.fav_suit = -1
        self.next_discard_idx = -1
        self.tricks_won = 0

    def add_cards(self, t: List):
        tot = len(self.hand) + len(t)
        if tot in (2, 3, 5):
            self.hand.extend(t)
        else:
            raise ValueError("Coming in HOT!")

    def all_perms(self) -> List[List[Card]]:
        perms: list[list[Card]] = []
        subset: list[Card]
        for i in range(5):
            subset = self.hand
            subset = self.swap(subset, i, 5)
            perms.append(subset)

        return perms

    def calculate(
        self, options: List[Tuple[Card, int]], played: List[Card], tricks: Score
    ) -> int:
        """Randomly select for now, will use ML later."""
        k: int = randrange(0, len(options))
        return options[k][1]

    def call_trump(self, top_card: Card, round: int, am_dealer: bool):
        t = Trump(-1, 0)
        if round == 1:
            if am_dealer:
                t = self.dealer_option(top_card=top_card)
            else:
                t = self.preferred_suit(top_card, round)
            return t
        else:
            t = self.preferred_suit(top_card, round)
            return t

    def fold(self):
        self.hand = []

    def dealer_option(self, top_card: Card) -> Trump:
        """Dealer's option to call trump by picking up the top card."""
        # goal - declare trump (OR NOT)
        t = Trump(-1, 0)

        # add the card and score your hand
        self.hand.append(top_card)
        top_suit = top_card.suit
        perms = self.all_perms()
        max_idx = -1
        max_score = 0.0
        for j in range(5):
            hand_score: float = self.score_hand(top_card.suit, perms[j])
            if hand_score > max_score:
                max_score = hand_score
                max_idx = j

            # call trump?
            if hand_score > LONER_PROBABILITY:
                t.suit = top_suit
                t.alone = 1
                max_idx = j
                break

            elif max_score > 2.5:
                t.suit = top_suit
                max_idx = j

        self.hand = self.swap(self.hand, max_idx, 5)
        self.hand.pop()  # discard

        # return the trump, if any
        return t

    def pick_it_up(self, top_card: Card) -> None:
        """The dealer acquires the top card.

        Two phases:
            1. Check to see if you even want the top suit to be trump
            2. If so, swap out your worst card for the top card and discard
        """
        # phase 1
        self.hand.append(top_card)
        top_suit = top_card.suit
        perms = self.all_perms()
        max_idx = -1
        max_score = 0.0
        for j in range(5):
            hand_score: float = self.score_hand(top_suit, perms[j])
            if hand_score > max_score:
                max_score = hand_score
                max_idx = j

        # phase 2
        self.hand = self.swap(self.hand, max_idx, 5)
        self.hand.pop()  # discard

    def play_card(
        self, leadsuit: int, trump: Trump, played: List, tricks: Score
    ) -> Card:
        options: List[Tuple[Card, int]] = []

        # first, follow suit
        if leadsuit >= 0:
            for idx, c in enumerate(self.hand):
                if c.suit == leadsuit or (
                    c.bauer == 0 and (c.suit + 2) % 4 == leadsuit
                ):
                    options.append((c, idx))

        # if you can't follow suit, all your options are available
        if len(options) == 0:
            options = [(c, i) for i, c in enumerate(self.hand)]

        best = self.calculate(options, played, tricks)

        last = len(self.hand) - 1
        if last > 0:
            self.hand = self.swap(self.hand, best, -1)

        b: Card = self.hand.pop()
        return b

    def gameplay(self, trump_suit: int):
        self.tricks_won = 0
        for c in self.hand:
            c.set_trump(trump_suit)
        pass

    def preferred_suit(self, top_card: Card, bid_round: int, dealer: bool = False):
        max_score = -1
        max_prob = 0.0
        max_idx_suit = -1
        t = Trump(-1, 0)
        top_suit = top_card.suit

        if bid_round == 1:
            if dealer:
                t = self.pick_it_up(top_card)

            else:
                hand_score: float = self.score_hand(top_suit)

                if hand_score > LONER_PROBABILITY:
                    t.suit = top_suit
                    t.alone = 1

                elif hand_score > 2.5:
                    t.suit = top_suit

        elif bid_round == 2:
            for i in range(4):
                if i == top_suit:
                    continue
                else:
                    hand_score = self.score_hand(i)
                    if hand_score > max_score:
                        max_score = hand_score
                        max_idx_suit = i

            # compare probabilities
            if max_prob > LONER_PROBABILITY:
                t.suit = max_idx_suit
                t.alone = 1

            elif max_score > 2.5:
                t.suit = max_idx_suit

        else:
            # bid round 3 - screw the dealer
            for i in range(4):
                if i == top_suit:
                    continue
                else:
                    hand_score = self.score_hand(i)
                    if hand_score > max_score:
                        max_score = hand_score
                        max_idx_suit = i

            t.suit = max_idx_suit

        return t

    def score_hand(self, trump_suit: int, tmp_hand: List[Card] = []) -> float:
        """Probability needs to be based on ability to win 3 tricks or 5"""

        tmp_hand = tmp_hand.copy() if len(tmp_hand) else self.hand.copy()
        score_ = 0
        for c in tmp_hand:
            c.set_trump(trump_suit)
            prob = (LEAD_PROBABILITIES[c.value] + FOLLOW_PROBS[c.value]) / 2
            # a super naive probability of how probs work
            score_ += prob * prob
            c.unset_trump()

        return score_

    def swap(self, l: List[Card], a: int, b: int) -> List[Card]:
        l[a], l[b] = l[b], l[a]
        return l

    def __repr__(self):
        out: str = ""
        for c in self.hand:
            out += repr(c)
