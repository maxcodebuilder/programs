print("Welcome to my game!")
name = input("What is your name? ")
age = int(input("What is your age? "))

health = 10

if age >= 10:
    print("You are old enough to play!")

    wants_to_play = input("Do you want to play? ").lower()
    if wants_to_play == "yes":
        print("You are starting with", health, "health")
        print("Let's play!")

        ans = input("First choice... North, South, East, or West (North/South/East/West)? ")
        if ans == "north":
            ans = input("Nice, you walk along a path and get to a cave. Do you explore the cave or go around (explore/around)? ")

            if ans == "explore":
                print("You found some money in a small hole but lost 5 health because you were bitten by a spider...")
                health -= 5
            if ans == "around":
                print("You went around the cave and found a merchant. He is willing to give you medicine in exchange for some money.")

            ans = input("You see a merchant. Do have money to trade with him? (yes/no) ")

            if ans == "yes":
                print("You got medicine and got 5 health")
                health += 5
            if ans == "no":
                print("Its okay that you do not have any money")

            ans = input("You see a house and a river, which do you go to? (house/river) ")
            if ans == "house":
                print("The owner is nice to you and takes you to a bathouse")

                ans = input("You can either go down the road or go into the bathouse. (road/bathouse) ")

                if ans == "road":
                    print("You tried to cross the road but you got hit by a car.")
                    print("You lost...")
                if ans == "bathouse":
                    print("You went into the bathouse.")

                    ans = input("You can either rest in the main room, ask for a free bath, or sneak in. (main/bath/sneak) ")

                    if ans == "main":
                        print("You rested and woke up in a bus.")

                        ans = input("Do you exit the bus at the next stop or do you wait for the stop after it? (first/second) ")

                        if ans == "first":
                            print("You forgot your hat on the bus so you went to get it but the door closed on you.")
                            print("You lost...")
                        if ans == "second":
                            print("You got off at an abandoned mineshaft.")

                            ans = input("Do you explore or go away? (explore/go away) ")

                            if ans == "explore":
                                print("You walked in and fell down a big hole.")
                                print("You lost...")
                            if ans == "go away":
                                print("You walk away into a rock which falls on you.")
                                print("You lost...")
                    if ans == "bath":
                        print("The company did not allow a free bath.")

                        ans = input("You spot a crowbar, do you steal it or just walk out of the building (steal/walk out)? ")

                        if ans == "steal":
                            print("You were spotted and killed")
                            print("You lost...")
                        if ans == "walk out":
                            print("You were sent to jail.")

                            ans = input("You are in jail, do you escape or stay (escape/stay)? ")

                            if "escape":
                                print("You were caught again and killed")
                                print("You lost...")
                            if "stay":
                                print("You died of thirst.")
                                print("You lost...")
                    if ans == "sneak":
                        print("You were spotted and kicked, you lost 5 health")
                        health -= 5

                        ans = input("Do you punch the receptionist or leave peacefully (punch/leave)? ")

                        if ans == "punch":
                            print("He was a sumo wrestler and you lost 5 health.")
                            health -= 5
                        if ans == "leave":
                            print("You were shot and you died")
                            print("You lost...")

                            if health <= 0:
                                print("You ran out of health")
                                print("You lost...")

            if ans == "river":
                print("You try to wash dirt off you body but you fell in and drowned.")
                print("You lost...")
            
        if ans == "south":

            ans = input("You see an arcade, do go into the arcade or continue on the path? (arcade/path) ")

            if ans == "arcade":
                print("You automatically go on an escalater and lose control of yourself, you fall on your face and fall out a window.")
                print("You lost...")
            if ans == "path":
                print("You walk along a path and find a lake.")

                ans = input("Do you swim across the lake or go around? (swim/go around) ")

                if ans == "swim":
                    print("You managed to swim across but you were bitten by an ant on the shore and lost 5 health.")
                    health -= 5

                    ans = input("You see a village and a well, which do you go to? (village/well) ")

                    if ans == "village":
                        print("The people turned out to be from Mars, and they threw a rock at you and you died.")
                        print("You lost...")
                    if ans == "well":
                        print("You drank but you were caught and you were attacked and lost 3 health.")
                        health -= 3

                        ans = input("You are trapped on an island, do you leave or stay?(leave/stay) ")

                        if ans == "leave":
                            print("You got caught in a storm and your ship sunk.")
                            print("You lost...")
                        if ans == "stay":
                            print("You decide to explore the island.")

                            ans = input("Do you go left or right? (left/right) ")

                            if ans == "left":
                                print("You found a family and they let you stay at their mansion.")

                                ans = input("You can go to your room or sneak into one of their rooms. (your room/their room) ")

                                if ans == "your room":
                                    print("You were tricked and you fell into a hole")
                                    print("You lost...")
                                if ans == "their room":
                                    print("The family said, 'So you have found out' and threw you out of the house, you lost 5 health.")
                                    health -= 5
                                    if health <= 0:
                                        print("You ran out of health.")
                                        print("You lost")

                            if ans == "right":
                                print("You find a pack of murderers and they killed you.")
                                print("You lost...")
                if ans == "around":
                    print("You tripped on a rock and fell into the sand, you ate some, choked, and died.")
                    print("You lost...")
        if ans == "east":
            print("You tripped and fell of a cliff to the center of the earth, you press a random button and the core turns into a trampoline.")

            ans = input("You see an open path and a door, do you take the open path or open the door? (path/door) ")

            if ans == "path":
                print("You fell and died")
            if ans == "door":
                print("You were blinded by a powerful light, went blind and fell of a cliff and died.")
                print("You lose")
        if ans == "west":
            print("You find a castle.")

            ans = input("Do you go in, or jump into the moat? (castle/moat) ")

            if ans == "castle":
                print("You are put into prison and fall into a lava pit while you try to escape.")
                print("You lost...")
            if ans == "moat":
                print("You found a leprachan that gives you a pot of gold if you answer his riddle correctly.")

                ans = input("What is the answer to my riddle: Mississippi has 4 s's and 4 i's, how do you spell that without any s's or i's? ")

                if ans == "T - H - A - T":
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                    print("You win!")
                else:
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")
                    print("You lost...")

    else:
        print(">:(")

else:
    print("You are not old enough to play...")