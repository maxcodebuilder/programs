import pygame
import random
import time

# Color codes for terminal output
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    PURPLE = "\033[95m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    RESET = "\033[0m"

class AdventureGame:
    def __init__(self):
        self.health = 100
        self.energy = 100
        self.gold = 0
        self.inventory = []
        self.story_events = 0
        self.choices_made = []
        
    def print_header(self, text):
        print(f"\n{Colors.CYAN}{'='*50}{Colors.RESET}")
        print(f"{Colors.CYAN}{text.center(50)}{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")
    
    def print_status(self):
        health_bar = "█" * (self.health // 10) + "░" * (10 - self.health // 10)
        energy_bar = "█" * (self.energy // 10) + "░" * (10 - self.energy // 10)
        
        print(f"{Colors.GREEN}Health: {health_bar} {self.health}/100{Colors.RESET}")
        print(f"{Colors.YELLOW}Energy: {energy_bar} {self.energy}/100{Colors.RESET}")
        print(f"{Colors.PURPLE}Gold: {self.gold} | Items: {len(self.inventory)}{Colors.RESET}\n")
    
    def encounter(self):
        """Generate random encounters"""
        encounters = {
            "merchant": self.merchant_encounter,
            "combat": self.combat_encounter,
            "mystery": self.mystery_encounter,
            "treasure": self.treasure_encounter,
            "puzzle": self.puzzle_encounter,
            "npc": self.npc_encounter,
        }
        
        encounter_type = random.choice(list(encounters.keys()))
        encounters[encounter_type]()
    
    def merchant_encounter(self):
        print(f"{Colors.BLUE}A hooded merchant appears on the road!{Colors.RESET}")
        print("Their cart is filled with mysterious wares...\n")
        
        items = [
            ("Health Potion", 30, lambda: self.use_potion("health")),
            ("Energy Drink", 25, lambda: self.use_potion("energy")),
            ("Mysterious Orb", 50, lambda: self.add_inventory("Mysterious Orb")),
            ("Ancient Map", 40, lambda: self.add_inventory("Ancient Map")),
        ]
        
        print("What do you do?")
        print("1) Buy an item")
        print("2) Rob the merchant")
        print("3) Leave peacefully")
        
        choice = input(f"\n{Colors.YELLOW}Choose (1-3): {Colors.RESET}").strip()
        
        if choice == "1":
            print("\nWhich item interests you?")
            for i, (name, cost, _) in enumerate(items, 1):
                print(f"{i}) {name} - {cost} gold")
            
            try:
                item_choice = int(input(f"\n{Colors.YELLOW}Choose (1-{len(items)}): {Colors.RESET}")) - 1
                if 0 <= item_choice < len(items):
                    name, cost, action = items[item_choice]
                    if self.gold >= cost:
                        self.gold -= cost
                        action()
                        print(f"{Colors.GREEN}Purchase complete!{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}Not enough gold!{Colors.RESET}")
                        print("The merchant scoffs and leaves.")
            except ValueError:
                print("Invalid choice. The merchant disappears.")
        
        elif choice == "2":
            if random.random() > 0.5:
                stolen = random.randint(10, 50)
                self.gold += stolen
                self.energy -= 20
                print(f"{Colors.GREEN}You steal {stolen} gold and escape!{Colors.RESET}")
            else:
                damage = random.randint(15, 30)
                self.health -= damage
                print(f"{Colors.RED}The merchant fights back! You take {damage} damage.{Colors.RESET}")
        
        else:
            print("The merchant tips his hat and moves on.")
    
    def combat_encounter(self):
        enemy_types = ["Goblin", "Bandit", "Wild Beast", "Shadow Creature", "Rogue Knight"]
        enemy = random.choice(enemy_types)
        enemy_health = random.randint(30, 60)
        
        print(f"{Colors.RED}A {enemy} appears!{Colors.RESET}")
        print(f"Enemy Health: {enemy_health}\n")
        print("What do you do?")
        print("1) Fight")
        print("2) Run away")
        print("3) Try to negotiate")
        
        choice = input(f"\n{Colors.YELLOW}Choose (1-3): {Colors.RESET}").strip()
        
        if choice == "1":
            while enemy_health > 0 and self.health > 0:
                damage = random.randint(5, 25)
                enemy_health -= damage
                enemy_damage = random.randint(3, 20)
                self.health -= enemy_damage
                
                print(f"You deal {damage} damage! Enemy has {max(0, enemy_health)} HP left.")
                print(f"The {enemy} deals {enemy_damage} damage to you!\n")
                time.sleep(0.5)
            
            if self.health > 0:
                reward = random.randint(20, 80)
                self.gold += reward
                self.energy -= 30
                print(f"{Colors.GREEN}Victory! You gain {reward} gold.{Colors.RESET}")
            else:
                print(f"{Colors.RED}You were defeated...{Colors.RESET}")
                self.health = 50
        
        elif choice == "2":
            if random.random() > 0.3:
                print(f"{Colors.YELLOW}You escape from the {enemy}!{Colors.RESET}")
                self.energy -= 10
            else:
                damage = random.randint(10, 20)
                self.health -= damage
                print(f"{Colors.RED}The {enemy} catches you! You take {damage} damage.{Colors.RESET}")
        
        else:
            if random.random() > 0.6:
                self.gold += random.randint(10, 30)
                print(f"{Colors.GREEN}The {enemy} was moved by your words and left you gold!{Colors.RESET}")
            else:
                damage = random.randint(12, 25)
                self.health -= damage
                print(f"{Colors.RED}Negotiation failed! The {enemy} attacks!{Colors.RESET}")
    
    def treasure_encounter(self):
        print(f"{Colors.BLUE}You discover a chest hidden in the ruins!{Colors.RESET}\n")
        print("The lock glows with magical energy...\n")
        
        print("1) Force it open")
        print("2) Search for a key")
        print("3) Leave it alone")
        
        choice = input(f"\n{Colors.YELLOW}Choose (1-3): {Colors.RESET}").strip()
        
        if choice == "1":
            if random.random() > 0.3:
                treasure = random.randint(50, 200)
                self.gold += treasure
                print(f"{Colors.GREEN}Treasure inside! You gain {treasure} gold!{Colors.RESET}")
            else:
                damage = random.randint(10, 25)
                self.health -= damage
                print(f"{Colors.RED}Trap! The chest explodes, dealing {damage} damage!{Colors.RESET}")
        
        elif choice == "2":
            if random.random() > 0.5:
                print(f"{Colors.GREEN}You find a key and open the chest safely!{Colors.RESET}")
                treasure = random.randint(80, 150)
                self.gold += treasure
                print(f"Inside: {treasure} gold and a mysterious artifact!")
                self.add_inventory("Mysterious Artifact")
            else:
                print(f"{Colors.YELLOW}After searching, you find nothing...{Colors.RESET}")
        
        else:
            print("You wisely move on.")
    
    def mystery_encounter(self):
        print(f"{Colors.PURPLE}A strange fog surrounds you...{Colors.RESET}\n")
        mysteries = [
            ("You see a figure in the mist. They vanish before you can approach.", 0),
            ("The fog parts, revealing a path you've never seen before.", 0),
            ("You hear whispers in an ancient language. You feel... wiser.", 0),
            ("Time seems to freeze. When normal flow resumes, hours have passed.", -20),
        ]
        
        event, energy_cost = random.choice(mysteries)
        print(event)
        if energy_cost < 0:
            self.energy += energy_cost
            print(f"\n{Colors.YELLOW}Energy: {self.energy}{Colors.RESET}")
        else:
            print("You feel nothing in particular.")
    
    def puzzle_encounter(self):
        print(f"{Colors.BLUE}An ancient stone tablet appears before you!{Colors.RESET}\n")
        
        puzzles = [
            ("What is 7 + 8?", "15", 25),
            ("What color is the ocean?", "blue", 15),
            ("How many sides does a triangle have?", "3", 20),
        ]
        
        question, answer, reward = random.choice(puzzles)
        print(f"Puzzle: {question}\n")
        
        user_answer = input(f"{Colors.YELLOW}Your answer: {Colors.RESET}").strip().lower()
        
        if user_answer == answer.lower():
            self.gold += reward
            print(f"{Colors.GREEN}Correct! You gain {reward} gold!{Colors.RESET}")
        else:
            print(f"{Colors.RED}Incorrect. The answer was '{answer}'.{Colors.RESET}")
    
    def npc_encounter(self):
        npcs = {
            "Wise Elder": "Tell me, what is the greatest treasure of all? The answer is friendship, young one.",
            "Tired Traveler": "I've walked these lands for 40 years. Every step was worth it.",
            "Mysterious Stranger": "I can see your future... it's bright, but challenging. Good luck.",
            "Cheerful Bard": "Would you hear a song? *plays a terrible tune*",
        }
        
        npc_name = random.choice(list(npcs.keys()))
        npc_quote = npcs[npc_name]
        
        print(f"{Colors.CYAN}You meet: {npc_name}{Colors.RESET}\n")
        print(f'"{npc_quote}"\n')
        print("1) Thank them and move on")
        print("2) Ask for help")
        
        choice = input(f"\n{Colors.YELLOW}Choose (1-2): {Colors.RESET}").strip()
        
        if choice == "2" and random.random() > 0.5:
            help_type = random.choice(["gold", "health", "energy"])
            if help_type == "gold":
                self.gold += 20
                print(f"{Colors.GREEN}They give you 20 gold!{Colors.RESET}")
            elif help_type == "health":
                self.health = min(100, self.health + 30)
                print(f"{Colors.GREEN}They heal your wounds!{Colors.RESET}")
            else:
                self.energy = min(100, self.energy + 25)
                print(f"{Colors.GREEN}They share their energy with you!{Colors.RESET}")
        else:
            print("They wish you well on your journey.")
    
    def use_potion(self, potion_type):
        if potion_type == "health":
            self.inventory.append("Health Potion")
        else:
            self.inventory.append("Energy Drink")
    
    def add_inventory(self, item):
        self.inventory.append(item)
    
    def use_inventory(self):
        if not self.inventory:
            print("You have no items to use.")
            return
        
        print("\nYour inventory:")
        for i, item in enumerate(self.inventory, 1):
            print(f"{i}) {item}")
        print(f"{len(self.inventory)+1}) Back")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}Choose item (1-{len(self.inventory)+1}): {Colors.RESET}")) - 1
            if choice == len(self.inventory):
                return
            elif 0 <= choice < len(self.inventory):
                item = self.inventory[choice]
                if item == "Health Potion":
                    self.health = min(100, self.health + 40)
                    print(f"{Colors.GREEN}Health restored!{Colors.RESET}")
                    self.inventory.pop(choice)
                elif item == "Energy Drink":
                    self.energy = min(100, self.energy + 35)
                    print(f"{Colors.GREEN}Energy restored!{Colors.RESET}")
                    self.inventory.pop(choice)
                else:
                    print(f"You examine the {item}... Nothing happens.")
        except ValueError:
            print("Invalid choice.")
    
    def play(self):
        self.print_header("MYSTICAL ADVENTURE")
        print("Welcome, adventurer! You find yourself in a land of mystery.\n")
        print("Your goal: Survive, explore, and accumulate as much gold as possible.\n")
        input(f"{Colors.YELLOW}Press Enter to begin...{Colors.RESET}")
        
        while self.health > 0:
            self.print_header(f"Adventure #{self.story_events + 1}")
            self.print_status()
            
            print("What do you do?")
            print("1) Explore the area")
            print("2) Check inventory")
            print("3) Rest (restore energy)")
            print("4) Quit game")
            
            choice = input(f"\n{Colors.YELLOW}Choose (1-4): {Colors.RESET}").strip()
            
            if choice == "1":
                self.encounter()
                self.story_events += 1
                
                if self.energy < 20:
                    print(f"\n{Colors.YELLOW}You're exhausted...{Colors.RESET}")
                    self.energy = max(0, self.energy - 20)
            
            elif choice == "2":
                self.use_inventory()
            
            elif choice == "3":
                if self.energy < 100:
                    self.energy = min(100, self.energy + 40)
                    print(f"{Colors.GREEN}You rest and feel refreshed!{Colors.RESET}")
                    self.story_events += 1
                else:
                    print("You're not tired.")
            
            elif choice == "4":
                break
            
            # Random passive damage/healing
            if random.random() > 0.7:
                passive_event = random.choice([
                    (f"{Colors.YELLOW}A cold wind passes by...{Colors.RESET}", -5),
                    (f"{Colors.GREEN}You find some berries to eat!{Colors.RESET}", 10),
                ])
                print(f"\n{passive_event[0]}")
                self.health = max(1, min(100, self.health + passive_event[1]))
            
            # Gradually drain energy
            self.energy = max(0, self.energy - random.randint(3, 8))
            
            if self.energy <= 0:
                print(f"\n{Colors.RED}You collapsed from exhaustion!{Colors.RESET}")
                self.health = max(1, self.health - 20)
                self.energy = 30
        
        self.print_header("GAME OVER")
        print(f"Final Stats:")
        print(f"Adventures: {self.story_events}")
        print(f"Gold collected: {self.gold}")
        print(f"Items found: {len(self.inventory)}")
        print(f"\n{Colors.CYAN}Thanks for playing!{Colors.RESET}\n")

if __name__ == "__main__":
    game = AdventureGame()
    game.play()
