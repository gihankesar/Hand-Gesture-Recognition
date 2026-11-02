def main():
    difficulty = input("Difficult or casual? ")
    players = input("Multiplayer or single-player? ")

    if difficulty == "Difficult":
        if players == "Multiplayer":
            recommend("poker")
        elif players == "single-player":
            recommend("klondike")
        else :
            print("Enter a valid answer")    
    elif difficulty == "casual":
        if players == "Multiplayer":
            recommend("hearts")
        elif players == "single-player":
            recommend("clock")
        else :
            print("Enter a valid answer")
    else :
            print("Enter a valid answer")        
def recommend(game):
    print("You might like", game)    

main()