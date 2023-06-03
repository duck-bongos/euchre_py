from random import randint, seed, shuffle

from src.card import Card
from src.player import Player


class Deck:
    def __init__(self):
        self.cards = [None] * 24
        self.build_deck()
        self.idx = 0

    def build_deck(self):
        self.idx = 0
        idx_ = 0
        for i in range(4):
            for j in range(9, 15):
                c = Card(j, i)
                self.cards[idx_] = c
                idx_ += 1

        r = randint(1, 1001)
        seed(r)
        shuffle(self.cards)

        reversed(self.cards)

    def deal_three(self):
        l = self.cards[self.idx : self.idx + 3]
        self.idx += 3
        return l

    def deal_two(self):
        l = self.cards[self.idx : self.idx + 2]
        self.idx += 2
        return l

    def pick_dealer(self) -> int:
        jack_found = False
        idx_ = 0
        dealer = -1
        while not jack_found:
            c = self.cards[idx_]
            if c.value == 11:
                jack_found = True
                dealer = idx_ % 4
            idx_ += 1
        return dealer

    def deal_cards(
        self, dealer_id: int, one: Player, two: Player, three: Player, four: Player
    ):
        order = (one, two, three, four)
        for i in range(8):
            player_id = (dealer_id + i) % 4

            if (i < 4 and i % 2 == 0) or (i >= 4 and i % 2 == 1):
                t = self.deal_three()

            elif (i < 4 and i % 2 == 1) or (i >= 4 and i % 2 == 0):
                t = self.deal_two()

            order[player_id].add_cards(t)

        # top card
        top_card = self.cards[self.idx + 1]
        return top_card
