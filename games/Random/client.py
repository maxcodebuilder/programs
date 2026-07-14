import pygame
import socket
import json
import threading
from enum import Enum

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 200)
DARK_GREY = (50, 50, 50)
LIGHT_GREY = (150, 150, 150)

class GameClient:
    def __init__(self, server_host='localhost', server_port=5555):
        pygame.init()
        
        self.WIDTH = 1000
        self.HEIGHT = 700
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Multiplayer Adventure - Pygame Server")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.player_id = None
        self.player_name = "Player"
        
        self.game_state = {
            "health": 100,
            "energy": 100,
            "gold": 0,
            "level": 1,
            "kills": 0,
            "messages": [],
            "players": [],
            "leaderboard": []
        }
        
        self.screen_state = "menu"  # menu, connecting, playing, leaderboard
        self.input_text = ""
        self.current_encounter = None
        
    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            
            # Start receiving thread
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            self.screen_state = "playing"
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def receive_messages(self):
        while True:
            try:
                data = self.socket.recv(1024).decode()
                if not data:
                    break
                
                message = json.loads(data)
                self.handle_message(message)
            except Exception as e:
                print(f"Receive error: {e}")
                break
    
    def handle_message(self, message):
        msg_type = message.get("type")
        
        if msg_type == "connection":
            self.player_id = message.get("player_id")
            self.add_message(f"Connected as Player {self.player_id}")
        
        elif msg_type == "encounter":
            player = message.get("player")
            encounter = message.get("encounter")
            self.current_encounter = encounter
            self.add_message(f"{player}: {encounter.get('description')}")
        
        elif msg_type == "achievement":
            player = message.get("player")
            msg = message.get("message")
            self.add_message(f"⭐ {player}: {msg}")
        
        elif msg_type == "death":
            player = message.get("player")
            self.add_message(f"💀 {player} was defeated!")
        
        elif msg_type == "leaderboard":
            self.game_state["leaderboard"] = message.get("board", [])
        
        elif msg_type == "player_list":
            self.game_state["players"] = message.get("players", [])
    
    def add_message(self, msg):
        self.game_state["messages"].append(msg)
        if len(self.game_state["messages"]) > 15:
            self.game_state["messages"].pop(0)
    
    def send_action(self, action_type, data=None):
        try:
            message = {"type": "action", "action": action_type}
            if data:
                message.update(data)
            self.socket.send(json.dumps(message).encode())
        except Exception as e:
            print(f"Send error: {e}")
    
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        title = self.font_large.render("Multiplayer Adventure", True, CYAN)
        self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 100))
        
        prompt = self.font_medium.render("Enter your name:", True, WHITE)
        self.screen.blit(prompt, (self.WIDTH // 2 - prompt.get_width() // 2, 250))
        
        # Draw input box
        input_box = pygame.Rect(self.WIDTH // 2 - 150, 320, 300, 50)
        pygame.draw.rect(self.screen, LIGHT_GREY, input_box)
        pygame.draw.rect(self.screen, CYAN, input_box, 2)
        
        text_surface = self.font_medium.render(self.input_text, True, BLACK)
        self.screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))
        
        instruction = self.font_small.render("Press ENTER to continue", True, YELLOW)
        self.screen.blit(instruction, (self.WIDTH // 2 - instruction.get_width() // 2, 450))
    
    def draw_connecting(self):
        self.screen.fill(BLACK)
        
        text = self.font_large.render("Connecting to server...", True, CYAN)
        self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2 - 50))
    
    def draw_playing(self):
        self.screen.fill(DARK_GREY)
        
        # Header
        header = self.font_large.render(f"Welcome, {self.player_name}!", True, CYAN)
        self.screen.blit(header, (20, 10))
        
        # Stats panel
        stats_x, stats_y = 20, 70
        stats = [
            f"Health: {self.game_state['health']}/100",
            f"Energy: {self.game_state['energy']}/100",
            f"Gold: {self.game_state['gold']}",
            f"Level: {self.game_state['level']}",
            f"Kills: {self.game_state['kills']}"
        ]
        
        for stat in stats:
            text = self.font_small.render(stat, True, YELLOW)
            self.screen.blit(text, (stats_x, stats_y))
            stats_y += 35
        
        # Current encounter
        encounter_y = 70
        encounter_text = self.font_medium.render("Current Encounter:", True, WHITE)
        self.screen.blit(encounter_text, (self.WIDTH // 2 + 100, encounter_y))
        
        if self.current_encounter:
            desc = self.font_small.render(self.current_encounter.get("description"), True, GREEN)
            self.screen.blit(desc, (self.WIDTH // 2 + 100, encounter_y + 50))
        else:
            idle = self.font_small.render("Nothing happening...", True, LIGHT_GREY)
            self.screen.blit(idle, (self.WIDTH // 2 + 100, encounter_y + 50))
        
        # Active players
        players_y = 300
        players_text = self.font_medium.render("Online Players:", True, WHITE)
        self.screen.blit(players_text, (self.WIDTH // 2 + 100, players_y))
        
        for i, player in enumerate(self.game_state["players"][:3]):
            player_line = f"• {player['name']} (Gold: {player['gold']})"
            text = self.font_small.render(player_line, True, PURPLE)
            self.screen.blit(text, (self.WIDTH // 2 + 120, players_y + 40 + i * 30))
        
        # Message log
        log_y = 80
        log_header = self.font_medium.render("Activity Feed:", True, WHITE)
        self.screen.blit(log_header, (20, log_y - 40))
        
        for message in self.game_state["messages"][-12:]:
            text = self.font_small.render(message, True, GREEN)
            self.screen.blit(text, (20, log_y))
            log_y += 28
        
        # Action buttons
        button_y = self.HEIGHT - 120
        self.draw_button("Encounter [E]", 20, button_y, 180, 40, RED)
        self.draw_button("Attack [A]", 220, button_y, 180, 40, RED)
        self.draw_button("Rest [R]", 420, button_y, 180, 40, YELLOW)
        self.draw_button("Leaderboard [L]", 620, button_y, 180, 40, CYAN)
    
    def draw_leaderboard(self):
        self.screen.fill(BLACK)
        
        title = self.font_large.render("Leaderboard", True, CYAN)
        self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 30))
        
        board_y = 100
        header = self.font_medium.render("Name".ljust(20) + "Gold".ljust(15) + "Kills", True, YELLOW)
        self.screen.blit(header, (100, board_y))
        board_y += 40
        
        for rank, (name, gold, kills) in enumerate(self.game_state["leaderboard"][:10], 1):
            entry = f"{rank}. {name}".ljust(20) + str(gold).ljust(15) + str(kills)
            color = GOLD_COLOR if rank == 1 else WHITE
            text = self.font_small.render(entry, True, color)
            self.screen.blit(text, (100, board_y))
            board_y += 35
        
        instruction = self.font_small.render("Press L to return to game", True, GREEN)
        self.screen.blit(instruction, (self.WIDTH // 2 - instruction.get_width() // 2, self.HEIGHT - 50))
    
    def draw_button(self, text, x, y, w, h, color):
        pygame.draw.rect(self.screen, color, (x, y, w, h))
        pygame.draw.rect(self.screen, WHITE, (x, y, w, h), 2)
        
        text_surface = self.font_small.render(text, True, WHITE)
        self.screen.blit(text_surface, (x + 10, y + 8))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.screen_state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.input_text.strip():
                        self.player_name = self.input_text
                        self.add_message(f"Connecting as {self.player_name}...")
                        self.screen_state = "connecting"
                        threading.Thread(target=self.connect_to_server).start()
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 20:
                            self.input_text += event.unicode
            
            elif self.screen_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.send_action("encounter")
                    elif event.key == pygame.K_a:
                        self.send_action("attack")
                    elif event.key == pygame.K_r:
                        self.send_action("rest")
                    elif event.key == pygame.K_l:
                        self.socket.send(json.dumps({"type": "get_leaderboard"}).encode())
                        self.screen_state = "leaderboard"
            
            elif self.screen_state == "leaderboard":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    self.screen_state = "playing"
        
        return True
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            
            if self.screen_state == "menu":
                self.draw_menu()
            elif self.screen_state == "connecting":
                self.draw_connecting()
            elif self.screen_state == "playing":
                self.draw_playing()
            elif self.screen_state == "leaderboard":
                self.draw_leaderboard()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        if self.socket:
            self.socket.close()
        pygame.quit()

GOLD_COLOR = (255, 215, 0)

if __name__ == "__main__":
    client = GameClient()
    client.run()
