from flask import Flask, render_template, redirect, url_for, session, request
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

#OOP CLASSES
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = self.get_value()

    def get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

class Deck:
    def __init__(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value
        if card.rank == 'A':
            self.aces += 1
        self.adjust_for_ace()

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

    def serialize(self):
        return [{'rank': c.rank, 'suit': c.suit} for c in self.cards]

def deserialize_hand(card_list):
    hand = Hand()
    for c in card_list:
        hand.add_card(Card(c['suit'], c['rank']))
    return hand

#ROUTES
@app.route('/')
def index():
    deck = Deck()
    player = Hand()
    dealer = Hand()

    for _ in range(2):
        player.add_card(deck.deal())
        dealer.add_card(deck.deal())

    session['deck'] = [(c.suit, c.rank) for c in deck.cards]
    session['player'] = player.serialize()
    session['dealer'] = dealer.serialize()
    session['player_value'] = player.value
    session['dealer_value'] = dealer.value

    return render_template('index.html',
        player=session['player'],
        dealer=session['dealer'],
        hide_dealer=True,
        value=player.value
    )

@app.route('/hit')
def hit():
    deck = [Card(s, r) for (s, r) in session['deck']]
    player = deserialize_hand(session['player'])

    player.add_card(deck.pop())

    session['deck'] = [(c.suit, c.rank) for c in deck]
    session['player'] = player.serialize()
    session['player_value'] = player.value

    if player.value > 21:
        return redirect(url_for('stand'))

    return render_template('index.html',
        player=session['player'],
        dealer=session['dealer'],
        hide_dealer=True,
        value=player.value
    )

@app.route('/stand', methods=['GET', 'POST'])
def stand():
    deck = [Card(s, r) for (s, r) in session['deck']]
    player = deserialize_hand(session['player'])
    dealer = deserialize_hand(session['dealer'])

    while dealer.value < 17:
        dealer.add_card(deck.pop())

    session['dealer'] = dealer.serialize()

    p_val = player.value
    d_val = dealer.value

    # Your desired logic:
    if p_val > 21:
        result = "You busted! Dealer wins."
    elif d_val > 21:
        result = "Dealer busted! You win."
    elif p_val > d_val:
        result = "You win!"
    elif p_val < d_val:
        result = "Dealer wins."
    else:
        result = "It's a tie!"

    return render_template('result.html',
        player=session['player'],
        dealer=session['dealer'],
        pvalue=p_val,
        dvalue=d_val,
        result=result
    )

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
