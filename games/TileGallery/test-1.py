import json
import os
import time
import pygame

pygame.init()

WIDTH, HEIGHT = 1024, 640
TILE_SIZE = 32
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tilemap + Pixel Art Editor")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 20)
BIG_FONT = pygame.font.SysFont(None, 28)

PIXEL_COLORS = [
    (30, 30, 30),   # black
    (240, 240, 240), # white
    (200, 50, 50),  # red
    (50, 200, 50),  # green
    (50, 50, 220),  # blue
    (240, 120, 200), # pink
    (160, 80, 200), # purple
    (180, 110, 40), # brown
    (120, 30, 30),  # maroon
    (240, 220, 80), # yellow
]

GALLERY_DIR = os.path.join(os.path.dirname(__file__), "tile_gallery")
GALLERY_THUMB_SIZE = 40
GALLERY_PADDING = 8
GALLERY_COLUMNS = 5


def draw_text(surface, text, x, y, color=(255, 255, 255), font=None):
    font = font or FONT
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x, y))


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def create_tile_surfaces():
    tiles = {}
    for index, color in enumerate(PIXEL_COLORS):
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surface.fill(color)
        tiles[index] = surface
    return tiles


def load_tilemap(filename):
    if not os.path.isfile(filename):
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def create_pixel_canvas(width, height, fill=0):
    return [[fill for _ in range(width)] for _ in range(height)]


def resize_pixel_canvas(canvas, new_width, new_height):
    old_height = len(canvas)
    old_width = len(canvas[0]) if old_height > 0 else 0
    new_canvas = create_pixel_canvas(new_width, new_height, fill=0)
    for y in range(min(old_height, new_height)):
        for x in range(min(old_width, new_width)):
            new_canvas[y][x] = canvas[y][x]
    return new_canvas


def save_pixel_art(filename_json, filename_png, canvas):
    data = {
        "width": len(canvas[0]),
        "height": len(canvas),
        "pixels": canvas,
    }
    with open(filename_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    surf = pygame.Surface((len(canvas[0]), len(canvas)))
    for y, row in enumerate(canvas):
        for x, color_index in enumerate(row):
            surf.set_at((x, y), PIXEL_COLORS[color_index])
    pygame.image.save(surf, filename_png)


def load_tile_gallery(directory):
    gallery = []
    if not os.path.isdir(directory):
        return gallery
    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(directory, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            pixels = data.get("pixels")
            if isinstance(pixels, list) and pixels:
                gallery.append({
                    "name": os.path.splitext(filename)[0],
                    "canvas": pixels,
                    "path": path,
                })
        except Exception:
            pass
    return gallery


def main():
    tiles = create_tile_surfaces()

    default_map = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 3, 0, 0, 0, 2, 2, 2, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]

    tilemap = load_tilemap(os.path.join(os.path.dirname(__file__), "tilemap.json")) or default_map
    pixel_canvas = create_pixel_canvas(32, 32)
    current_color = 1
    current_size = 32
    zoom = 12
    saved_message = ""
    save_message_timer = 0.0
    canvas_area = pygame.Rect(660, 300, 340, 320)
    gallery_area = pygame.Rect(24, 440, 592, 160)
    editing = False

    os.makedirs(GALLERY_DIR, exist_ok=True)
    saved_tiles = load_tile_gallery(GALLERY_DIR)
    gallery_selected = 0 if saved_tiles else -1
    loaded_tile_path = None

    camera_x = 0
    camera_y = 0
    speed = 200

    running = True
    while running:
        dt = CLOCK.tick(60) / 1000.0
        save_message_timer = max(0.0, save_message_timer - dt)
        if save_message_timer <= 0:
            saved_message = ""

        canvas_zoom = clamp(zoom, 1, min(canvas_area.width // current_size, canvas_area.height // current_size))
        canvas_width_px = current_size * canvas_zoom
        canvas_height_px = current_size * canvas_zoom
        canvas_x = canvas_area.x + (canvas_area.width - canvas_width_px) // 2
        canvas_y = canvas_area.y + (canvas_area.height - canvas_height_px) // 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    pixel_canvas = create_pixel_canvas(current_size, current_size)
                elif event.key == pygame.K_r:
                    tilemap = [row.copy() for row in pixel_canvas]
                    saved_message = "Custom tilemap loaded"
                    save_message_timer = 2.0
                elif event.key == pygame.K_e:
                    if gallery_selected >= 0 and loaded_tile_path:
                        save_pixel_art(loaded_tile_path, loaded_tile_path.replace(".json", ".png"), pixel_canvas)
                        saved_message = f"Updated {saved_tiles[gallery_selected]['name']}"
                        save_message_timer = 2.0
                elif event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                    saved_name = f"tile_{int(time.time() * 1000)}"
                    save_pixel_art(
                        os.path.join(GALLERY_DIR, f"{saved_name}.json"),
                        os.path.join(GALLERY_DIR, f"{saved_name}.png"),
                        pixel_canvas,
                    )
                    save_pixel_art(
                        os.path.join(os.path.dirname(__file__), "pixel_art.json"),
                        os.path.join(os.path.dirname(__file__), "pixel_art.png"),
                        pixel_canvas,
                    )
                    saved_tiles = load_tile_gallery(GALLERY_DIR)
                    gallery_selected = len(saved_tiles) - 1
                    if gallery_selected >= 0:
                        loaded_tile_path = saved_tiles[gallery_selected]["path"]
                    saved_message = f"Saved {saved_name}.json"
                    save_message_timer = 2.0
                elif event.key == pygame.K_LEFTBRACKET:
                    new_size = clamp(current_size - 4, 4, 320)
                    pixel_canvas = resize_pixel_canvas(pixel_canvas, new_size, new_size)
                    current_size = new_size
                elif event.key == pygame.K_RIGHTBRACKET:
                    new_size = clamp(current_size + 4, 4, 320)
                    pixel_canvas = resize_pixel_canvas(pixel_canvas, new_size, new_size)
                    current_size = new_size
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    zoom = clamp(zoom + 1, 1, 24)
                elif event.key == pygame.K_MINUS:
                    zoom = clamp(zoom - 1, 1, 24)
                elif event.key == pygame.K_UP:
                    if saved_tiles:
                        if gallery_selected < 0:
                            gallery_selected = 0
                        row = gallery_selected // GALLERY_COLUMNS
                        col = gallery_selected % GALLERY_COLUMNS
                        if row > 0:
                            row -= 1
                        new_index = row * GALLERY_COLUMNS + col
                        gallery_selected = min(new_index, len(saved_tiles) - 1)
                        loaded_canvas = saved_tiles[gallery_selected]["canvas"]
                        loaded_tile_path = saved_tiles[gallery_selected]["path"]
                        current_size = len(loaded_canvas[0])
                        pixel_canvas = [row.copy() for row in loaded_canvas]
                        saved_message = f"Selected {saved_tiles[gallery_selected]['name']}"
                        save_message_timer = 1.5
                elif event.key == pygame.K_DOWN:
                    if saved_tiles:
                        if gallery_selected < 0:
                            gallery_selected = 0
                        row = gallery_selected // GALLERY_COLUMNS
                        col = gallery_selected % GALLERY_COLUMNS
                        row += 1
                        new_index = row * GALLERY_COLUMNS + col
                        gallery_selected = min(new_index, len(saved_tiles) - 1)
                        loaded_canvas = saved_tiles[gallery_selected]["canvas"]
                        loaded_tile_path = saved_tiles[gallery_selected]["path"]
                        current_size = len(loaded_canvas[0])
                        pixel_canvas = [row.copy() for row in loaded_canvas]
                        saved_message = f"Selected {saved_tiles[gallery_selected]['name']}"
                        save_message_timer = 1.5
                elif event.key == pygame.K_LEFT:
                    if saved_tiles:
                        if gallery_selected < 0:
                            gallery_selected = 0
                        if gallery_selected % GALLERY_COLUMNS > 0:
                            gallery_selected -= 1
                        loaded_canvas = saved_tiles[gallery_selected]["canvas"]
                        loaded_tile_path = saved_tiles[gallery_selected]["path"]
                        current_size = len(loaded_canvas[0])
                        pixel_canvas = [row.copy() for row in loaded_canvas]
                        saved_message = f"Selected {saved_tiles[gallery_selected]['name']}"
                        save_message_timer = 1.5
                elif event.key == pygame.K_RIGHT:
                    if saved_tiles:
                        if gallery_selected < 0:
                            gallery_selected = 0
                        if gallery_selected < len(saved_tiles) - 1:
                            gallery_selected += 1
                        loaded_canvas = saved_tiles[gallery_selected]["canvas"]
                        loaded_tile_path = saved_tiles[gallery_selected]["path"]
                        current_size = len(loaded_canvas[0])
                        pixel_canvas = [row.copy() for row in loaded_canvas]
                        saved_message = f"Selected {saved_tiles[gallery_selected]['name']}"
                        save_message_timer = 1.5
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    current_color = event.key - pygame.K_1
                elif event.key == pygame.K_0:
                    current_color = 9
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and gallery_area.collidepoint(*event.pos):
                    mouse_x, mouse_y = event.pos
                    rel_x = mouse_x - gallery_area.x
                    rel_y = mouse_y - gallery_area.y
                    col = rel_x // (GALLERY_THUMB_SIZE + GALLERY_PADDING)
                    row = rel_y // (GALLERY_THUMB_SIZE + GALLERY_PADDING)
                    index = int(row * GALLERY_COLUMNS + col)
                    if 0 <= index < len(saved_tiles):
                        gallery_selected = index
                        loaded_canvas = saved_tiles[index]["canvas"]
                        loaded_tile_path = saved_tiles[index]["path"]
                        current_size = len(loaded_canvas[0])
                        pixel_canvas = [row.copy() for row in loaded_canvas]
                        zoom = clamp(zoom, 1, min(canvas_area.width // current_size, canvas_area.height // current_size))
                        saved_message = f"Loaded {saved_tiles[index]['name']}"
                        save_message_timer = 2.0
                elif event.button in (1, 3):
                    mouse_x, mouse_y = event.pos
                    if canvas_x <= mouse_x < canvas_x + canvas_width_px and canvas_y <= mouse_y < canvas_y + canvas_height_px:
                        editing = True
                        click_color = current_color if event.button == 1 else 0
                        cell_x = (mouse_x - canvas_x) // canvas_zoom
                        cell_y = (mouse_y - canvas_y) // canvas_zoom
                        if 0 <= cell_x < current_size and 0 <= cell_y < current_size:
                            pixel_canvas[cell_y][cell_x] = click_color
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (1, 3):
                    editing = False
            elif event.type == pygame.MOUSEMOTION and editing:
                mouse_x, mouse_y = event.pos
                if canvas_x <= mouse_x < canvas_x + canvas_width_px and canvas_y <= mouse_y < canvas_y + canvas_height_px:
                    cell_x = (mouse_x - canvas_x) // canvas_zoom
                    cell_y = (mouse_y - canvas_y) // canvas_zoom
                    if 0 <= cell_x < current_size and 0 <= cell_y < current_size:
                        pixel_canvas[cell_y][cell_x] = current_color

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            camera_x -= speed * dt
        if keys[pygame.K_d]:
            camera_x += speed * dt
        if keys[pygame.K_w]:
            camera_y -= speed * dt
        if keys[pygame.K_s]:
            camera_y += speed * dt

        SCREEN.fill((18, 18, 18))

        # Draw tilemap panel
        pygame.draw.rect(SCREEN, (22, 22, 22), (10, 10, 620, 620))
        draw_text(SCREEN, "Tilemap Example", 24, 18, font=BIG_FONT)
        draw_text(SCREEN, "Use WASD to pan this tilemap; arrows move saved selection.", 24, 46)
        for row_index, row in enumerate(tilemap):
            for col_index, tile_id in enumerate(row):
                tile = tiles.get(tile_id, tiles[0])
                x = 24 + col_index * TILE_SIZE + int(camera_x)
                y = 80 + row_index * TILE_SIZE + int(camera_y)
                SCREEN.blit(tile, (x, y))

        # Draw pixel art editor panel
        pygame.draw.rect(SCREEN, (22, 22, 22), (640, 10, 374, 620))
        draw_text(SCREEN, "Pixel Art Editor", 656, 18, font=BIG_FONT)
        draw_text(SCREEN, f"Canvas: {current_size} x {current_size}", 656, 46)
        draw_text(SCREEN, f"Selected color: {current_color + 1}", 656, 66)
        draw_text(SCREEN, "Controls:", 656, 100)
        draw_text(SCREEN, "1-0: change brush color", 656, 122)
        draw_text(SCREEN, "[: smaller canvas, ]: larger canvas", 656, 142)
        draw_text(SCREEN, "- / +: zoom view", 656, 162)
        draw_text(SCREEN, "Left-click: paint, Right-click: erase", 656, 182)
        draw_text(SCREEN, "C: clear, R: load art as tilemap", 656, 202)
        draw_text(SCREEN, "E: save changes, Ctrl+S: save as new", 656, 222)
        if saved_message:
            draw_text(SCREEN, saved_message, 656, 246, color=(180, 255, 180))

        # Draw palette
        for i, color in enumerate(PIXEL_COLORS):
            row = i // 5
            col = i % 5
            rect = pygame.Rect(656 + col * 40, 250 + row * 40, 32, 32)
            pygame.draw.rect(SCREEN, color, rect)
            if i == current_color:
                pygame.draw.rect(SCREEN, (255, 255, 255), rect, 3)
            else:
                pygame.draw.rect(SCREEN, (100, 100, 100), rect, 1)

        # Draw tile gallery below tilemap
        pygame.draw.rect(SCREEN, (28, 28, 28), gallery_area)
        draw_text(SCREEN, "Saved Tile Gallery", gallery_area.x + 4, gallery_area.y + 4)
        for index, tile in enumerate(saved_tiles):
            row = index // GALLERY_COLUMNS
            col = index % GALLERY_COLUMNS
            thumb_x = gallery_area.x + col * (GALLERY_THUMB_SIZE + GALLERY_PADDING)
            thumb_y = gallery_area.y + 24 + row * (GALLERY_THUMB_SIZE + GALLERY_PADDING)
            thumb_rect = pygame.Rect(thumb_x, thumb_y, GALLERY_THUMB_SIZE, GALLERY_THUMB_SIZE)
            pygame.draw.rect(SCREEN, (40, 40, 40), thumb_rect)
            if index == gallery_selected:
                pygame.draw.rect(SCREEN, (255, 255, 255), thumb_rect, 3)
            else:
                pygame.draw.rect(SCREEN, (100, 100, 100), thumb_rect, 1)

            saved_canvas = tile["canvas"]
            thumb_w = len(saved_canvas[0])
            thumb_h = len(saved_canvas)
            thumb_scale = max(1, min(GALLERY_THUMB_SIZE // thumb_w, GALLERY_THUMB_SIZE // thumb_h))
            for ty, row_data in enumerate(saved_canvas):
                for tx, color_index in enumerate(row_data):
                    if tx >= GALLERY_THUMB_SIZE or ty >= GALLERY_THUMB_SIZE:
                        break
                    color = PIXEL_COLORS[color_index] if 0 <= color_index < len(PIXEL_COLORS) else PIXEL_COLORS[0]
                    pixel_rect = pygame.Rect(
                        thumb_x + tx * thumb_scale,
                        thumb_y + ty * thumb_scale,
                        thumb_scale,
                        thumb_scale,
                    )
                    pygame.draw.rect(SCREEN, color, pixel_rect)

        # Draw pixel canvas below palette so max-size art remains visible
        pygame.draw.rect(SCREEN, (56, 56, 56), (660, 366, 340, 2))

        # Render pixel canvas
        canvas_zoom = clamp(zoom, 1, min(canvas_area.width // current_size, canvas_area.height // current_size))
        canvas_width_px = current_size * canvas_zoom
        canvas_height_px = current_size * canvas_zoom
        canvas_x = canvas_area.x + (canvas_area.width - canvas_width_px) // 2
        canvas_y = canvas_area.y + (canvas_area.height - canvas_height_px) // 2

        pygame.draw.rect(SCREEN, (50, 50, 50), (canvas_x - 2, canvas_y - 2, canvas_width_px + 4, canvas_height_px + 4))
        for y, row in enumerate(pixel_canvas):
            for x, color_index in enumerate(row):
                rect = pygame.Rect(canvas_x + x * canvas_zoom, canvas_y + y * canvas_zoom, canvas_zoom, canvas_zoom)
                pygame.draw.rect(SCREEN, PIXEL_COLORS[color_index], rect)
                pygame.draw.rect(SCREEN, (30, 30, 30), rect, 1)

        draw_text(SCREEN, f"Zoom: {canvas_zoom}x", 656, 580)
        draw_text(SCREEN, "Saved to pixel_art.json / pixel_art.png", 656, 600, color=(180, 180, 180))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
