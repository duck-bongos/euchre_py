from random import randint
from typing import List

from .card import Card
from .utils import BestCard, HandScore, Score, Trump

LONER_PROBABILITY = 85


class Player:
    def __init__(self) -> None:
        self.team = 0
        self.name = "Player Zero"
        self.hand: List[Card] = []
        self.fav_suit = -1
        self.next_discard_idx = -1

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

    def calculate(self, options: List[Card], played: List[Card], tricks: Score):
        k: int = 0
        for i in range(len(options)):
            if options[i].value > 8 and (options[i].value > options[k].value):
                k = i

        bc = BestCard(options[k], k)
        return bc

    def call_trump(self, top_card: Card, round: int, am_dealer: bool):
        round_one_suit = top_card.suit
        t = Trump(-1, 0)
        if round == 1:
            if am_dealer:
                self.hand.append(top_card)
                t = self.preferred_suit(round_one_suit, round)
                self.hand.pop()
            else:
                t = self.preferred_suit(round_one_suit, round)
            return t
        else:
            t = self.preferred_suit(round_one_suit, round)
            return t

    def fold(self):
        self.hand = []

    def pick_it_up(self, top_card: Card) -> None:
        self.hand.append(top_card)
        perms = self.all_perms()
        one_max_score = 0
        for j in range(5):
            hs: HandScore = self.score_hand(top_card.suit, perms[j])
            if hs.score > one_max_score:
                one_max_score = hs.score
                one_max_prob = hs.prob
                one_max_idx = j
        self.hand = self.swap(self.hand, one_max_idx, 5)
        self.hand.pop()
        return

    def play_card(
        self, leadsuit: int, trump: Trump, played: List, tricks: Score
    ) -> Card:
        options = []

        if leadsuit >= 0:
            for c in self.hand:
                if c.suit == leadsuit:
                    options.append(c)

        if len(options) == 0:
            options = self.hand

        best = self.calculate(options, played, tricks)

        last = len(self.hand) - 1
        if last > 0:
            self.hand = self.swap(self.hand, best.idx, -1)

        b: Card = self.hand.pop()
        return b

    def preferred_suit(self, top_suit: int, bid_round: int):
        max_score = -1
        max_idx_suit = -1
        t = Trump(-1, 0)

        for i in range(4):
            if i == top_suit and bid_round > 1:
                continue

            else:
                hs = self.score_hand(i)
                if bid_round == 3:
                    if hs.score > max_score:
                        max_idx_suit = i
                        max_score = hs.score
                    else:
                        if hs.score > max_score and (hs.prob > (randint(1, 101))):
                            max_idx_suit = i
                            max_score = hs.score
                            if hs.score > max_score and hs.prob > LONER_PROBABILITY:
                                t.alone = 1
                                break
            t.suit = max_idx_suit
            return t

    def round_one(self, top_suit: int, round: int):
        perms = self.all_perms()
        t = Trump(-1, 0)
        one_max_score = -1
        one_max_prob = 0.0
        one_max_idx = -1

        for j in range(5):
            hs: HandScore = self.score_hand(top_suit, perms[j])
            if hs.score > one_max_score:
                one_max_score = hs.score
                one_max_prob = hs.prob
                one_max_idx = j

        if one_max_prob > randint(1, 101):
            self.hand = self.swap(self.hand, one_max_idx, -1)
            if one_max_prob > LONER_PROBABILITY:
                t = Trump(top_suit, 1)

            else:
                t = Trump(top_suit, 0)
        return t

    def score_hand(self, trump_suit: int, tmp_hand: List[Card] = []):
        tmp_hand = tmp_hand if len(tmp_hand) else self.hand
        s = 0
        p = 0.0
        for c in tmp_hand:
            c.set_trump(trump_suit)
            s += c.value
            c.unset_trump()

        p = (s / 115.0) * 100.0
        hs = HandScore(s, p)
        return hs

    def swap(self, l: List[Card], a: int, b: int) -> List[Card]:
        l[a], l[b] = l[b], l[a]
        return l

    def __repr__(self):
        out: str = ""
        for c in self.hand:
            out += repr(c)
