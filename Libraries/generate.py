import random 

# coin = random.choice(["heads","tails"])
# print(coin)
# number = random.randint(1,10)
# print(number)

cards = ["queen", "King", "Joker"]
random.shuffle(cards)
for card in cards:
    print(card)