from random import randint
from typing import List

from src.card import Card
from src.deck import Deck
from src.player import Player
from src.utils import Score, Trump


def tally_score(
    score: Score, tricks: Score, who_called_trump: str, who_called_alone: int
):
    loner = 2 if who_called_alone != "" else 1
    if tricks.odds == 3 or tricks.odds == 4:
        if who_called_trump == "Odds":
            score.odds += 1
        else:
            # euchred
            score.odds += 2
    elif tricks.evens == 3 or tricks.evens == 4:
        if who_called_trump == "Evens":
            score.evens += 1
        else:
            score.evens += 2
    elif tricks.odds == 5 and who_called_trump == "Odds":
        score.odds += 2 * loner

    elif tricks.odds == 5 and who_called_trump == "Evens":
        score.odds += 2  # euchred

    elif tricks.evens == 5 and who_called_trump == "Evens":
        score.evens += 2 * loner

    elif tricks.evens == 5 and who_called_trump == "Odds":
        score.evens += 2  # euchred

    return score


def who_wins(trick: List):
    winner = 0
    for i in range(len(trick)):
        if trick[i].value > trick[winner].value:
            winner = i

    return winner


def show_hands(players: List[List[Card]], top_card: Card):
    for player in players:
        for c in player.hand:
            print(c)
        print()
    print(top_card)


def play(gameID: int):
    deck = Deck()
    dealer = deck.pick_dealer()
    leader: int = (dealer + 1) % 4
    r = randint(0, 1000)
    one = Player()
    two = Player()
    three = Player()
    four = Player()
    one.name = "Player One"
    two.name = "Player Two"
    three.name = "Player Three"
    four.name = "Player Four"

    score = Score(0, 0)
    tricks = Score(0, 0)

    order = (one, two, three, four)
    for i in range(4):
        if i % 2 == 1:
            order[i].team = "Evens"
        else:
            order[i].team = "Odds"

    while score.evens < 10 and score.odds < 10:
        print(f"Evens: {score.evens} Odds: {score.odds}")
        top_card: Card = deck.deal_cards(dealer, one, two, three, four)
        print(f"Dealer: {order[dealer].name} \nLeader: {order[leader].name}")
        trump = Trump(-1, 0)
        who_called_trump = -1

        loner_idx = -1
        skip_partner = -1
        round = 1
        screw_the_dealer = 0
        bidder_idx = 0
        i_called_trump = ""

        show_hands(order, top_card)

        # bidding round 1
        for i in range(4):
            bidder_idx = (leader + i) % 4
            partner_idx = (bidder_idx + 2) % 4
            trump = order[bidder_idx].call_trump(
                top_card, 1, am_dealer=bool(bidder_idx == dealer)
            )
            if trump.suit >= 0:
                order[dealer].pick_it_up(top_card)
                print(f"{order[bidder_idx].name} called trump!")
                who_called_trump = order[bidder_idx].team
                i_called_trump = order[bidder_idx].name
                print(f"Team {who_called_trump} picked up the {repr(top_card)}!")
                if trump.alone > 0:
                    skip_partner = partner_idx
                    print(
                        f"{order[bidder_idx].name} is going alone! {order[partner_idx].name} is folding."
                    )
                    order[partner_idx].fold()
                    break

        # bidding round 2
        if trump.suit >= 0:
            print(trump)
        else:
            round = 2
            for i in range(4):
                bidder_idx = (leader + 1) % 4
                partner_idx = (bidder_idx + 2) % 4

                trump = order[bidder_idx].call_trump(top_card, 2, am_dealer=False)
                if i == 3:
                    round = 3
                    trump = order[bidder_idx].call_trump(top_card, 3, am_dealer=False)
                    if trump.alone > 0:
                        who_called_trump = order[bidder_idx].team
                        i_called_trump = order[bidder_idx].name
                        skip_partner = partner_idx
                        order[skip_partner].fold()
                    assert trump.suit >= 0
                    break

                elif trump.suit >= 0:
                    who_called_trump = order[bidder_idx].team
                    i_called_trump = order[bidder_idx].name
                    if trump.alone > 0:
                        skip_partner = partner_idx
                        order[bidder_idx].fold()
                    break

        # play one hand
        show_hands(order, top_card)
        print(trump)
        for i in range(5):
            lead_suit = -1
            played = []

            # play one trick
            for j in range(4):
                player_idx = (leader + j) % 4
                partner_idx = (player_idx + 2) % 4
                if player_idx == skip_partner:
                    print(f"Skipping {order[player_idx].name} due to loner.")
                    continue

                else:
                    p = order[player_idx]
                    c = p.play_card(lead_suit, trump, played, tricks)
                    if i == 0:
                        lead_suit = c.suit
                    played.append(c)

            winner_idx = who_wins(played)

            leader = winner_idx
            team = order[winner_idx].team
            if team == "Evens":
                tricks.evens += 1
            else:
                tricks.odds += 1

            if (tricks.odds == 3 and tricks.evens == 1) or (
                tricks.evens == 3 and tricks.odds == 1
            ):
                for i in range(4):
                    order[i].fold()
                break

        alone = ""
        if loner_idx > 0:
            alone = order[loner_idx].team

        score = tally_score(score, tricks, who_called_trump, alone)
        tricks.evens = 0
        tricks.odds = 0
        print(f"Score: {score}")

        dealer = (dealer + 1) % 4
        leader = (dealer + 1) % 4

        deck.build_deck()

    if score.evens > score.odds:
        print(f"\nFinal Score: {score}\nEvens win!\n\n")
    else:
        print(f"\nFinal Score: {score}\nOdds win!\n\n")


if __name__ in "__main__":
    game_id = 0
    while game_id < 1:
        play(game_id)
        game_id += 1
