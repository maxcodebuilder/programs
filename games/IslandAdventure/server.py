import socket
import threading
import json
import random
import time
import pygame

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

class GameServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players = {}
        self.game_state = {
            "current_encounter": None,
            "leaderboard": []
        }
        self.lock = threading.Lock()
        
        # Pygame setup
        pygame.init()
        self.WIDTH = 1200
        self.HEIGHT = 700
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Game Server Dashboard")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        self.running = True
        self.start_time = time.time()
        
    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"[SERVER] Started on {self.host}:{self.port}")
        print("[SERVER] Waiting for connections...")
        
        # Run server socket listening in background
        threading.Thread(target=self.accept_connections, daemon=True).start()
        
        # Run pygame dashboard in main thread
        self.run_dashboard()
    
    def accept_connections(self):
        try:
            while self.running:
                self.server.settimeout(1)
                try:
                    client_socket, addr = self.server.accept()
                    print(f"[CONNECTION] New player from {addr}")
                    threading.Thread(target=self.handle_player, args=(client_socket, addr)).start()
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.server.close()
    
    def handle_player(self, client_socket, addr):
        player_id = str(len(self.players) + 1)
        
        with self.lock:
            self.players[player_id] = {
                "addr": addr,
                "socket": client_socket,
                "name": f"Player{player_id}",
                "health": 100,
                "energy": 100,
                "gold": 0,
                "level": 1,
                "kills": 0,
                "connected": True
            }
        
        try:
            # Send player ID to client
            self.send_to_player(client_socket, {
                "type": "connection",
                "player_id": player_id
            })
            
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                message = json.loads(data)
                self.process_message(player_id, message)
        
        except Exception as e:
            print(f"[ERROR] Player {player_id}: {e}")
        
        finally:
            with self.lock:
                if player_id in self.players:
                    self.players[player_id]["connected"] = False
                    del self.players[player_id]
            client_socket.close()
            print(f"[DISCONNECT] Player {player_id} disconnected")
    
    def process_message(self, player_id, message):
        msg_type = message.get("type")
        
        if msg_type == "set_name":
            with self.lock:
                if player_id in self.players:
                    self.players[player_id]["name"] = message.get("name", f"Player{player_id}")
        
        elif msg_type == "action":
            action = message.get("action")
            with self.lock:
                player = self.players.get(player_id)
                if not player:
                    return
                
                if action == "encounter":
                    encounter = self.generate_encounter()
                    self.broadcast({
                        "type": "encounter",
                        "player": player["name"],
                        "encounter": encounter
                    })
                
                elif action == "attack":
                    target_gold = random.randint(10, 50)
                    player["gold"] += target_gold
                    if player["gold"] > 0:
                        player["kills"] += 1
                    
                    self.broadcast({
                        "type": "achievement",
                        "player": player["name"],
                        "message": f"Defeated an enemy! +{target_gold} gold"
                    })
                
                elif action == "rest":
                    player["energy"] = min(100, player["energy"] + 40)
                    player["health"] = min(100, player["health"] + 20)
                
                elif action == "take_damage":
                    damage = message.get("damage", 10)
                    player["health"] -= damage
                    if player["health"] <= 0:
                        player["health"] = 50
                        self.broadcast({
                            "type": "death",
                            "player": player["name"]
                        })
        
        elif msg_type == "get_leaderboard":
            with self.lock:
                leaderboard = sorted(
                    [(p["name"], p["gold"], p["kills"]) for p in self.players.values()],
                    key=lambda x: x[1],
                    reverse=True
                )
            
            self.send_to_player(self.players[player_id]["socket"], {
                "type": "leaderboard",
                "board": leaderboard
            })
        
        elif msg_type == "get_players":
            with self.lock:
                player_list = [
                    {
                        "name": p["name"],
                        "gold": p["gold"],
                        "health": p["health"],
                        "level": p["level"]
                    }
                    for p in self.players.values()
                ]
            
            self.send_to_player(self.players[player_id]["socket"], {
                "type": "player_list",
                "players": player_list
            })
    
    def generate_encounter(self):
        encounters = [
            {"type": "merchant", "description": "A hooded merchant appears"},
            {"type": "combat", "description": "A fierce goblin attacks!"},
            {"type": "treasure", "description": "You found a treasure chest!"},
            {"type": "npc", "description": "A wandering sage greets you"},
            {"type": "mystery", "description": "Strange lights dance in the distance"},
        ]
        return random.choice(encounters)
    
    def broadcast(self, message):
        with self.lock:
            for player in self.players.values():
                try:
                    self.send_to_player(player["socket"], message)
                except:
                    pass
    
    def send_to_player(self, client_socket, message):
        try:
            client_socket.send(json.dumps(message).encode())
        except:
            pass
    
    def run_dashboard(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.draw_dashboard()
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
    
    def draw_dashboard(self):
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_large.render("Game Server Dashboard", True, CYAN)
        self.screen.blit(title, (20, 10))
        
        # Server info
        uptime = int(time.time() - self.start_time)
        uptime_text = self.font_small.render(f"Uptime: {uptime}s | Port: {self.port}", True, YELLOW)
        self.screen.blit(uptime_text, (20, 70))
        
        # Player stats
        with self.lock:
            total_players = len(self.players)
            total_gold = sum(p.get("gold", 0) for p in self.players.values())
            total_kills = sum(p.get("kills", 0) for p in self.players.values())
        
        stats_y = 120
        stats = [
            f"Connected Players: {total_players}",
            f"Total Gold Earned: {total_gold}",
            f"Total Kills: {total_kills}"
        ]
        
        for stat in stats:
            text = self.font_medium.render(stat, True, GREEN)
            self.screen.blit(text, (20, stats_y))
            stats_y += 50
        
        # Player list
        players_y = 350
        header = self.font_medium.render("Online Players:", True, WHITE)
        self.screen.blit(header, (20, players_y))
        players_y += 40
        
        with self.lock:
            for player_id, player in sorted(self.players.items()):
                info = f"[{player_id}] {player['name']} - Gold: {player['gold']} | Health: {player['health']}/100 | Kills: {player['kills']}"
                text = self.font_small.render(info, True, PURPLE)
                self.screen.blit(text, (40, players_y))
                players_y += 30
        
        # Legend
        legend_y = self.HEIGHT - 40
        legend = self.font_small.render("Close this window to stop the server", True, LIGHT_GREY)
        self.screen.blit(legend, (20, legend_y))

if __name__ == "__main__":
    server = GameServer()
    server.start()
