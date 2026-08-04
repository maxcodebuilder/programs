import pygame
import sys
import math
import random
import array

# Initialize Pygame and Audio Mixer safely
pygame.init()
HAS_AUDIO = True
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
except Exception:
    HAS_AUDIO = False  # Continues safely if no audio hardware is found

# Game Constants
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chomp Designer Pro: Stable Canvas Edition")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREY = (200, 200, 200)
DARK_GREY = (60, 60, 60)
PINK = (255, 105, 180)
RED = (230, 40, 40)
ORANGE = (255, 140, 0)
YELLOW = (255, 215, 0)
GREEN = (50, 205, 50)
BLUE = (30, 144, 255)
PURPLE = (147, 112, 219)

PALETTE = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, PINK, BLACK]
BUTTON_ZONE_HEIGHT = 120
CANVAS_HEIGHT = HEIGHT - BUTTON_ZONE_HEIGHT

def generate_crunch_sound():
    """Generates an 8-bit procedural crisp bite sound safely using list initialization."""
    if not HAS_AUDIO:
        return None
    try:
        sample_rate = 22050
        duration = 0.15  
        num_samples = int(sample_rate * duration)
        
        # FIXED: Initialized cleanly to eliminate low-level compilation crashes
        buf = array.array('h', [0] * num_samples)
        
        for i in range(num_samples):
            noise = random.randint(-12000, 12000)
            wave = int(math.sin(i * 0.05) * 8000 * (1.0 - (i / num_samples)))
            combined = int((noise + wave) * 0.4)
            buf[i] = max(-32768, min(32767, combined))
            
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

CRUNCH_SOUND = generate_crunch_sound()

class CandyCanvas:
    def __init__(self):
        self.canvas_surface = pygame.Surface((WIDTH, CANVAS_HEIGHT))
        self.clear_canvas()
        self.current_color = RED
        self.brush_size = 16
        self.is_drawing = False
        self.last_pos = None
        self.active_tool = "BRUSH" 

    def clear_canvas(self):
        self.canvas_surface.fill(WHITE)

    def draw_brush(self, pos):
        """Draws onto the surface safely by converting absolute window coordinates to relative canvas space."""
        # FIXED: Only process coordinate pairs if they sit safely inside the canvas limits
        if pos[1] < CANVAS_HEIGHT:
            relative_pos = (pos[0], pos[1])
            if self.active_tool == "BRUSH":
                if self.last_pos and self.last_pos[1] < CANVAS_HEIGHT:
                    pygame.draw.line(self.canvas_surface, self.current_color, self.last_pos, relative_pos, self.brush_size)
                    pygame.draw.circle(self.canvas_surface, self.current_color, relative_pos, self.brush_size // 2)
                else:
                    pygame.draw.circle(self.canvas_surface, self.current_color, relative_pos, self.brush_size // 2)
                self.last_pos = relative_pos
        else:
            # If the mouse slips into the UI menu area, immediately break the line link
            self.last_pos = None

    def apply_stamp(self, pos):
        """Draws structural decoration stamps safely inside canvas limits."""
        if pos[1] >= CANVAS_HEIGHT:
            return
        
        cx, cy = pos
        if self.active_tool == "SPRINKLE":
            angle = random.uniform(0, math.pi)
            sx = int(math.cos(angle) * 12)
            sy = int(math.sin(angle) * 12)
            pygame.draw.line(self.canvas_surface, self.current_color, (cx - sx, cy - sy), (cx + sx, cy + sy), 6)
            
        elif self.active_tool == "STAR":
            points = []
            for i in range(10):
                r = 16 if i % 2 == 0 else 7
                angle = i * math.pi / 5 - math.pi / 2
                points.append((cx + int(math.cos(angle) * r), cy + int(math.sin(angle) * r)))
            pygame.draw.polygon(self.canvas_surface, self.current_color, points)
            
        elif self.active_tool == "HEART":
            pygame.draw.circle(self.canvas_surface, self.current_color, (cx - 7, cy - 5), 8)
            pygame.draw.circle(self.canvas_surface, self.current_color, (cx + 7, cy - 5), 8)
            tri_points = [(cx - 15, cy - 2), (cx + 15, cy - 2), (cx, cy + 14)]
            pygame.draw.polygon(self.canvas_surface, self.current_color, tri_points)

    def stop_drawing(self):
        self.is_drawing = False
        self.last_pos = None


class BiteAnimationEngine:
    def __init__(self, raw_candy_surface):
        self.candy_image = raw_candy_surface.copy()
        self.width = self.candy_image.get_width()
        self.height = self.candy_image.get_height()
        
        self.bite_progress = 0.0
        self.max_bites = 6
        self.bite_positions = []
        self.bite_radius = 90
        self.is_finished = False
        self.last_triggered_index = -1
        
        self.generate_bite_path()

    def generate_bite_path(self):
        start_x = WIDTH // 4
        end_x = (WIDTH // 4) * 3
        for i in range(self.max_bites):
            step_ratio = i / (self.max_bites - 1)
            target_x = int(start_x + (end_x - start_x) * step_ratio)
            target_y = (CANVAS_HEIGHT // 2) + int(math.sin(i * 1.5) * 60)
            self.bite_positions.append((target_x, target_y))

    def update(self):
        if self.is_finished:
            return

        self.bite_progress += 0.035
        current_bite_index = int(self.bite_progress)

        if current_bite_index >= self.max_bites:
            self.is_finished = True
            return

        if current_bite_index > self.last_triggered_index:
            if CRUNCH_SOUND:
                CRUNCH_SOUND.play()
            self.last_triggered_index = current_bite_index

        pos = self.bite_positions[current_bite_index]
        fractional_part = self.bite_progress - current_bite_index
        if fractional_part < 0.4:
            current_radius = int(self.bite_radius * (fractional_part / 0.4))
            pygame.draw.circle(self.candy_image, WHITE, pos, current_radius)

    def draw(self, surface):
        surface.blit(self.candy_image, (0, 0))
        
        current_bite_index = int(self.bite_progress)
        if current_bite_index < self.max_bites and not self.is_finished:
            fractional_part = self.bite_progress - current_bite_index
            if fractional_part < 0.4:
                pos = self.bite_positions[current_bite_index]
                pygame.draw.circle(surface, PINK, pos, int(self.bite_radius * 1.1), 8)
                pygame.draw.circle(surface, WHITE, pos, int(self.bite_radius * 0.95), 12)


def main():
    canvas = CandyCanvas()
    animation_engine = None
    state = "DRAWING"

    eat_btn = pygame.Rect(WIDTH - 180, HEIGHT - 65, 150, 45)
    clear_btn = pygame.Rect(WIDTH - 350, HEIGHT - 65, 150, 45)
    reset_game_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 75, 200, 50)

    tool_rects = {
        "BRUSH": pygame.Rect(580, HEIGHT - 105, 85, 35),
        "SPRINKLE": pygame.Rect(675, HEIGHT - 105, 100, 35),
        "STAR": pygame.Rect(785, HEIGHT - 105, 80, 35),
        "HEART": pygame.Rect(875, HEIGHT - 105, 90, 35)
    }

    font = pygame.font.SysFont("Arial", 18, bold=True)
    heading_font = pygame.font.SysFont("Arial", 36, bold=True)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if state == "DRAWING":
                        # Check Tool Button intersections first
                        tool_clicked = False
                        for t_name, t_rect in tool_rects.items():
                            if t_rect.collidepoint(mouse_pos):
                                canvas.active_tool = t_name
                                tool_clicked = True
                                break
                        
                        if tool_clicked:
                            continue

                        # Check Function Button intersections
                        if eat_btn.collidepoint(mouse_pos):
                            animation_engine = BiteAnimationEngine(canvas.canvas_surface)
                            state = "EATING"
                        elif clear_btn.collidepoint(mouse_pos):
                            canvas.clear_canvas()
                        elif mouse_pos[1] >= CANVAS_HEIGHT:
                            # Check Color Swatch selection safely inside the dashboard zone
                            for idx, color in enumerate(PALETTE):
                                color_rect = pygame.Rect(30 + (idx * 60), HEIGHT - 65, 45, 45)
                                if color_rect.collidepoint(mouse_pos):
                                    canvas.current_color = color
                                    break
                        else:
                            # Process pure canvas drawing safely
                            if canvas.active_tool == "BRUSH":
                                canvas.is_drawing = True
                                canvas.draw_brush(mouse_pos)
                            else:
                                canvas.apply_stamp(mouse_pos)
                                
                    elif state == "EATING":
                        if animation_engine.is_finished and reset_game_btn.collidepoint(mouse_pos):
                            canvas.clear_canvas()
                            state = "DRAWING"

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    canvas.stop_drawing()

            elif event.type == pygame.MOUSEMOTION:
                if canvas.is_drawing and state == "DRAWING":
                    canvas.draw_brush(mouse_pos)

        # Rendering Sequence
        screen.fill(DARK_GREY)

        # Draw the canvas area
        screen.blit(canvas.canvas_surface, (0, 0))

        # Draw the UI dashboard area
        pygame.draw.rect(screen, GREY, (0, CANVAS_HEIGHT, WIDTH, BUTTON_ZONE_HEIGHT))
        pygame.draw.line(screen, BLACK, (0, CANVAS_HEIGHT), (WIDTH, CANVAS_HEIGHT), 4)

        # Draw Color Swatches
        for idx, color in enumerate(PALETTE):
            color_rect = pygame.Rect(30 + (idx * 60), HEIGHT - 65, 45, 45)
            pygame.draw.rect(screen, color, color_rect)
            if canvas.current_color == color:
                pygame.draw.rect(screen, BLACK, color_rect, 3)

        # Draw Tool Buttons
        for t_name, t_rect in tool_rects.items():
            pygame.draw.rect(screen, DARK_GREY, t_rect)
            tool_text = font.render(t_name, True, WHITE)
            text_rect = tool_text.get_rect(center=t_rect.center)
            screen.blit(tool_text, text_rect)

        # Draw Function Buttons
        pygame.draw.rect(screen, DARK_GREY, eat_btn)
        eat_text = font.render("EAT CANDY", True, WHITE)
        eat_text_rect = eat_text.get_rect(center=eat_btn.center)
        screen.blit(eat_text, eat_text_rect)

        pygame.draw.rect(screen, DARK_GREY, clear_btn)
        clear_text = font.render("CLEAR CANVAS", True, WHITE)
        clear_text_rect = clear_text.get_rect(center=clear_btn.center)
        screen.blit(clear_text, clear_text_rect)

        if state == "EATING" and animation_engine:
            animation_engine.update()
            animation_engine.draw(screen)

            if animation_engine.is_finished:
                pygame.draw.rect(screen, DARK_GREY, reset_game_btn)
                reset_text = font.render("RESET GAME", True, WHITE)
                reset_text_rect = reset_text.get_rect(center=reset_game_btn.center)
                screen.blit(reset_text, reset_text_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main() 
    