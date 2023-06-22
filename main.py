"""Main module to record results."""
from typing import List

from pymongo import MongoClient

from src.card import Card
from src.deck import Deck
from src.player import Player
from src.utils import Score, Trump
from src.record import Record


def get_collection():
    CONNECTION_STRING = "mongodb://localhost:27017"
    client = MongoClient(CONNECTION_STRING)
    database = client["euchre"]
    games = database["games"]
    return games


def tally_score(
    score: Score, tricks: Score, who_called_trump: str, who_called_alone: int
):
    loner = 2 if who_called_alone != "" else 1
    if tricks.odds == 3 or tricks.odds == 4:
        if who_called_trump == "Odds":
            score.odds += 1
        else:
            # euchred
            print("Evens got euchred!")
            score.odds += 2
    elif tricks.evens == 3 or tricks.evens == 4:
        if who_called_trump == "Evens":
            score.evens += 1
        else:
            score.evens += 2
    elif tricks.odds == 5 and who_called_trump == "Odds":
        score.odds += 2 * loner

    elif tricks.odds == 5 and who_called_trump == "Evens":
        print("Evens got euchred!")
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
    h = ["", "", "", "", ""]
    s = ""
    for player in players:
        for i, c in enumerate(player.hand):
            h[i] += f"{str(c)}\t\t"
    print("\n".join(h))
    print(f"Top Card: {top_card}")


def play(game_id: int):
    print(f"Game ID: {game_id}")
    deck = Deck()
    dealer = deck.pick_dealer()
    leader: int = (dealer + 1) % 4
    zero = Player()
    one = Player()
    two = Player()
    three = Player()
    one.name = "Player One"
    two.name = "Player Two"
    three.name = "Player Three"

    mongo_connection = get_collection()

    score = Score(0, 0)
    tricks = Score(0, 0)

    order = (zero, one, two, three)
    for i in range(4):
        if i % 2 == 1:
            order[i].team = "Odds"
        else:
            order[i].team = "Evens"

    while score.evens < 10 and score.odds < 10:
        top_card: Card = deck.deal_cards(dealer, zero, one, two, three)

        trump = Trump(-1, 0)
        who_called_trump = ""

        loner_idx = -1
        skip_partner = -1
        round = 1
        bidder_idx = 0
        i_called_trump = ""

        # bidding round 1
        for i in range(4):
            bidder_idx = (leader + i) % 4
            partner_idx = (bidder_idx + 2) % 4
            trump = order[bidder_idx].call_trump(
                top_card, 1, am_dealer=bool(bidder_idx == dealer)
            )

            if trump.suit >= 0:
                order[dealer].pick_it_up(top_card)

                who_called_trump = order[bidder_idx].team
                i_called_trump = order[bidder_idx].name

                if trump.alone > 0:
                    skip_partner = partner_idx
                    order[partner_idx].fold()
                    break

        # bidding round 2
        if trump.suit < 0:
            round = 2
            for i in range(4):
                bidder_idx = (leader + i) % 4
                partner_idx = (bidder_idx + 2) % 4

                trump = order[bidder_idx].call_trump(top_card, round, am_dealer=False)
                if trump.suit >= 0:
                    who_called_trump = order[bidder_idx].team
                    i_called_trump = order[bidder_idx].name
                    break
                if i == 3:
                    round = 3
                    trump = order[bidder_idx].call_trump(
                        top_card, round, am_dealer=True
                    )
                    who_called_trump = order[bidder_idx].team
                    i_called_trump = order[bidder_idx].name
                    if trump.alone > 0:
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

        print(f"{i_called_trump} calls {str(trump)}")

        # prepare to play
        for player_ in order:
            # set trump, set tricks = 0
            player_.gameplay(trump.suit)

        hand_number = 1
        for i in range(5):
            lead_suit = -1
            played = []
            played_ = []

            # play one trick
            for j in range(4):
                player_idx = (leader + j) % 4
                partner_idx = (player_idx + 2) % 4

                data = {
                    "hand_num": hand_number,
                    "players": [
                        {"hand": player.hand, "id": i, "tricks_won": player.tricks_won}
                        for i, player in enumerate(order)
                    ],
                    "trump": trump,
                    "trump_bidder_idx": bidder_idx,
                    "round": round,
                    "lead_suit": lead_suit,
                    "dealer": dealer,
                    "turn_idx": player_idx,
                    "score": score,
                    "current_trick": played_,
                }
                record = Record(data)

                r = record()
                try:
                    mongo_connection.insert_one(r)
                except Exception as e:
                    print(f"EXCEPTION: {e}")

                # Skip due to loner
                if player_idx == skip_partner:
                    continue

                else:
                    c = order[player_idx].play_card(lead_suit, trump, played, tricks)
                    if j == 0:
                        lead_suit = c.suit
                    played.append(c)
                    played_.append({"player_id": player_idx, "card": repr(c)})
            winner_idx = (who_wins(played) + leader) % 4
            order[winner_idx].tricks_won += 1

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
        print(f"Score: {score} | Tricks: {tricks}")
        tricks.evens = 0
        tricks.odds = 0

        dealer = (dealer + 1) % 4
        leader = (dealer + 1) % 4

        deck.build_deck()

    if score.evens > score.odds:
        print(f"\nFinal Score: {score}\nEvens win!\n\n")
    else:
        print(f"\nFinal Score: {score}\nOdds win!\n\n")


if __name__ in "__main__":
    game_id = 0
    while game_id < 500:
        play(game_id)
        game_id += 1
