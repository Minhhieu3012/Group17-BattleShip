import pygame
from common import Button
import os

class SetupScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 28)

        self.ready_button = Button(300, 500, 200, 50, "Ready")

        # Grid
        self.grid_size = 10
        self.cell_size = 40
        self.grid_origin = (100, 100)

        # Ship data (filename, length)
        self.ships_data = [
            ("image1.png", 2),
            ("image2.png", 3),
            ("image3.png", 4),
            ("image4.png", 5),
            ("image5.png", 3),
        ]
        self.ships = []

        image_folder = os.path.join(os.path.dirname(__file__), "images")

        start_x = self.grid_origin[0] + self.grid_size * self.cell_size + 50
        start_y = 100
        gap = 20

        for idx, (filename, length) in enumerate(self.ships_data):
            path = os.path.join(image_folder, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (length * self.cell_size, self.cell_size))
                rect = img.get_rect()
                rect.topleft = (start_x, start_y + idx * (rect.height + gap))

                self.ships.append({
                    "img": img,
                    "rect": rect,
                    "length": length,
                    "placed": False,
                    "grid_pos": None,
                })

        # Dragging
        self.dragging_ship = None
        self.offset_x = 0
        self.offset_y = 0

        self.done = False
        self.next = None

    def handle_event(self, event):
        if self.ready_button.handle_event(event):
            placed_ships = []
            for ship in self.ships:
                if ship["placed"]:
                    placed_ships.append({
                        "length": ship["length"],
                        "pos": ship["grid_pos"],   # (row, col)
                        "orientation": "H"         # hiện giờ chỉ ngang
                    })

            self.placed_ships = placed_ships   # <--- Lưu lại để BattleScreen dùng
            self.send_queue.put({
                "action": "ready",
                "user": self.username,
                "ships": placed_ships
            })
            self.done = True
            self.next = "battle"


        if event.type == pygame.MOUSEBUTTONDOWN:
            for ship in self.ships:
                if ship["rect"].collidepoint(event.pos):
                    self.dragging_ship = ship
                    mx, my = event.pos
                    self.offset_x = ship["rect"].x - mx
                    self.offset_y = ship["rect"].y - my
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_ship:
                mx, my = event.pos

                # --- LẤY TỌA ĐỘ GÓC TRÁI TRÊN ---
                ship_x, ship_y = self.dragging_ship["rect"].topleft

                # Tính col/row theo góc trái trên
                col = round((ship_x - self.grid_origin[0]) / self.cell_size)
                row = round((ship_y - self.grid_origin[1]) / self.cell_size)

                length = self.dragging_ship["length"]

                # --- KIỂM TRA HỢP LỆ ---
                if (0 <= col <= self.grid_size - length
                        and 0 <= row < self.grid_size):
                    # Snap đúng 3/4/5 ô liên tiếp
                    snap_x = self.grid_origin[0] + col * self.cell_size
                    snap_y = self.grid_origin[1] + row * self.cell_size
                    self.dragging_ship["rect"].topleft = (snap_x, snap_y)
                    self.dragging_ship["placed"] = True
                    self.dragging_ship["grid_pos"] = (row, col)  # góc trái trên
                else:
                    # Trả về dock (nếu đặt sai)
                    idx = self.ships.index(self.dragging_ship)
                    self.dragging_ship["rect"].topleft = (
                        self.grid_origin[0] + self.grid_size * self.cell_size + 50,
                        100 + idx * (self.cell_size + 20)
                    )
                    self.dragging_ship["placed"] = False
                    self.dragging_ship["grid_pos"] = None

                self.dragging_ship = None


        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_ship:
                mx, my = event.pos
                self.dragging_ship["rect"].x = mx + self.offset_x
                self.dragging_ship["rect"].y = my + self.offset_y

    def draw(self):
        self.screen.fill((30, 30, 60))

        # Title
        title = self.font.render(f"Setup Ships - {self.username}", True, (255, 255, 255))
        self.screen.blit(title, (250, 30))

        # Grid
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                rect = pygame.Rect(
                    self.grid_origin[0] + col * self.cell_size,
                    self.grid_origin[1] + row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

        # Ships
        for ship in self.ships:
            self.screen.blit(ship["img"], ship["rect"])

        # Ready button
        self.ready_button.draw(self.screen)

        pygame.display.flip()
    def update(self):
        pass
