name = input ("What is your name? ")
year2 = input ("What year is it? ")
year = input ("You were born in (year)")
age = int(year2) - int(year)
print ("Your name is", name, "and you are", str(age), "years old.")
if age <= 10:
    print ("You are old enough to play this game.")
    ans = input ("Do you want to play? (yes/no) ")
    if ans == "yes":
        print ("Let's play!")
        ans = input("You are trapped in a caastle, do you want to go left or right? (left/right) ")
        if ans == "left":
            ans = input("You go to the next room and find a coffin, do you want to open it? (yes/no) ")
            if ans == "yes":
                ans = input("You find a key inside the coffin that teleports you to the next room, and there is a door that leads you outside, do you go outside (yes/no) ")
                if ans == "yes":
                    print ("You are trapped because it was a trap, and a monster eats you, game over!")
                if ans == "no":
                    print("You have one of the keys to open a large safe which is said to give you one wish.")
                    ans = input("You see a room with a large dragon guarding the pathway to the next room, do you walk up boldly or cautiously? (boldly/cautiously) ")
                    if ans == "boldly":
                        print("The dragon takes this as a threat and eats you, game over!")
                    if ans == "cautiously":
                        input("The dragon sees you as no threat and lets you pass, taking you to the next room")
                        ans = input("You go into a maze in the next room, do you go left or right? (left/right) ")
                        if ans == "left":
                            print("You found another key to the safe, but you are in a dead end")
                            ans = input("Do you go back or stay in the dead end? (back/stay) ")
                            if ans == "back":
                                print("You go back to the previous room and find a door that leads you outside, but it was a trap and you are eaten by a monster, game over!")
                            if ans == "stay":
                                print("A secret door opens and you find another key to the safe!")
                                ans = input("Do you open the safe or go back to the previous room? (open/back) ")
                                if ans == "open":
                                    print("You open the safe and make a wish to be teleported outside, but it was a trap and you are eaten by a monster, game over!")
                                if ans == "back":
                                    print("You go back to the previous room and went into a portal that took you outside, you are free, congratulations, you win!")
                                    print("You have completed the game, thank you for playing!")
                                    print("If you want to play again, please restart the game.")
                                    print("If you want to play a different game, please go back to the main menu.")
                                    print("If you want to exit the game, please close the program.")
                                    print("If you want to give feedback, please contact the developer.")
                                    print("If you want to report a bug, please contact the developer.")
                                    print("If you want to suggest a feature, please contact the developer.")
                                    print("If you want to donate, please contact the developer.")
                                    print("If you want to support the developer, please contact the developer.")
                                    print("If you want to follow the developer, please contact the developer.")
                                    print("If you want to see more games, please contact the developer.")
                                    print("If you want to see more programs, please contact the developer.")
                                    print("If you want to see more projects, please contact the developer.")
                                    print("If you want to see more content, please contact the developer.")
                                    print("If you want to see more updates, please contact the developer.")
                                    print("If you want to see more news, please contact the developer.")
                                    print("If you want to see more information, please contact the developer.")
                        if ans == "right":
                            print("You fell down a trapdoor and died, game over!")
            if ans == "no":
                print("Since you didn't open the coffin, you are trapped in the room and die of starvation, game over!")
        if ans == "right":
            print("You go to the next room and accaidentally fall into the dungeon and died, game over!")
    if ans == "no":
        print("Maybe next time, but have a good day!")
else:
    print("You are not old enough to play this game, have a good day!")