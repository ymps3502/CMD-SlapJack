#!/usr/bin/python
import os
import time
import threading
import random
from random import shuffle
from collections import deque

NEXT_CARD = 0
DECK = []
FINISHED = 1
STEAL = False
GAMEOVER = False


class player(threading.Thread):
    """docstring for player"""

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.cards = self.get3cards()
        self.score = {'finish': 0, 'color': 0, 'number': 0, 'steal': 0}

    def run(self):
        while len(self.cards) != 0 and not GAMEOVER:
            delay = random.random()
            threadLock.acquire()
            # snap card if card has same number or color
            if match_card(self.cards) is not None:
                print self.name + " get the card!"
                snap_card(self.cards, match_card(self.cards), self.score)
                time.sleep(delay)
                print_all_players_card()
            elif STEAL:
                # steal card
                print self.name + " steal the card!"
                steal_card(self.cards, self.score)
                time.sleep(delay)
                print_all_players_card()
            threadLock.release()

    def get3cards(self):
        # get 3 cards from the deck
        cards = []
        global DECK
        for card in list(DECK):
            if len(cards) < 3:
                cards.append(DECK.pop())
            else:
                return cards

    def showCards(self, name, cards):
        if len(cards) == 0:
            print name + " is finished!"
        else:
            print name + ':\t' + unicard(cards)


def unicard(cards):
    color = "0123"
    string = ""
    if isinstance(cards, int):
        # cards is integer
        string += '\\u266{0}'.format(color[cards / 13])
        number = cards % 13 + 1
        if number == 11:
            string += 'J'
        elif number == 12:
            string += 'Q'
        elif number == 13:
            string += 'K'
        else:
            string += str(number)
    else:
        # cards is list
        for c in cards:
            string += '\\u266{0}'.format(color[c / 13])
            number = c % 13 + 1
            if number == 11:
                string += 'J'
            elif number == 12:
                string += 'Q'
            elif number == 13:
                string += 'K'
            else:
                string += str(number)
            string += '\t'
    return string.decode('unicode-escape')


def match_card(cards):
    for card in cards:
        global NEXT_CARD
        if NEXT_CARD / 13 == card / 13 or NEXT_CARD % 13 == card % 13:
            return card


def snap_card(cards, matchCard, score):
    # drop the card
    cards.remove(matchCard)
    # count  score
    global FINISHED
    global NEXT_CARD
    if NEXT_CARD / 13 == matchCard / 13:
        score['color'] += 1
    if NEXT_CARD % 13 == matchCard % 13:
        score['number'] += 1
    if len(cards) == 0 and FINISHED == 1:
        score['finish'] = 1
        FINISHED = 2
    if len(cards) == 0 and FINISHED == 2 and score['finish'] != 1:
        score['finish'] = 2
        FINISHED = 3
    # show next card from the deck
    try:
        NEXT_CARD = DECK.pop()
    except IndexError:
        global GAMEOVER
        GAMEOVER = True


def steal_card(cards, score):
    # add the card
    global NEXT_CARD
    cards.append(NEXT_CARD)
    score['steal'] += 1
    try:
        NEXT_CARD = DECK.pop()
    except IndexError:
        global GAMEOVER
        GAMEOVER = True


def print_all_players_card():
    time.sleep(2)
    allPlayersCard = list()
    os.system('clear')
    print "Deck left: " + str(len(DECK))
    print "-------------------------------------------------------------------"
    for t in threads:
        allPlayersCard.extend(t.cards)
        if len(t.cards) == 0:
            print t.name + ":\tfinish!"
        else:
            print t.name + ":\t" + unicard(t.cards)
    global STEAL
    if match_card(allPlayersCard) is not None:
        STEAL = False
    else:
        STEAL = True
    print "-------------------------------------------------------------------"
    if GAMEOVER:
        print "Next card: "
    else:
        print "Next card: " + unicard(NEXT_CARD)


def count_score():
    print "\tRank\tSteal\tSame Number\tSame Color\tTotal"
    for t in threads:
        total = 0
        msg = t.name + ":\t"
        if t.score['finish'] == 1:
            msg += "First\t"
            total += 50
        elif t.score['finish'] == 2:
            msg += "Second\t"
            total += 20
        else:
            msg += "--\t"
        total += t.score['steal'] * 5 + \
            t.score['number'] * 30 + t.score['color'] * 10
        msg += "{0:>5}\t".format(t.score['steal'])
        msg += "{0:>11}\t".format(t.score['number'])
        msg += "{0:>10}\t".format(t.score['color'])
        msg += "{0:>5}".format(total)
        print msg


threadLock = threading.Lock()
threads = []


if __name__ == "__main__":
    os.system('clear')
    # Create deck
    DECK = [i for i in range(52)]
    shuffle(DECK)
    DECK = deque(DECK)

    # Create new threads
    t1 = player("Amy")
    t2 = player("Bruce")
    t3 = player("Cally")
    t4 = player("David")

    # Add threads to thread list
    threads.append(t1)
    threads.append(t2)
    threads.append(t3)
    threads.append(t4)

    NEXT_CARD = DECK.pop()
    print_all_players_card()
    time.sleep(1)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print "Game over!\n"
    count_score()
