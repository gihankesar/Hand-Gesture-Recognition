def main():
    difficulty = input("Difficult or casual? ")
    players = input("Multiplayer or single-player? ")

    if not (difficulty == "Difficult" or difficulty == "casual"):
        print("Enter valid difficulty")
        return
    if not (players == "Multiplayer" or players == "single-player"):
        print("Enter valid players")
        return

    if difficulty == "Difficult" and players == "Multiplayer":
            recommend("poker")
    elif difficulty == "Difficult" and players == "single-player":
            recommend("klondike")
    elif difficulty == "casual" and players == "Multiplayer":
            recommend("hearts")
    else:  
            recommend("clock")
       
def recommend(game):
    print("You might like", game)    

main()