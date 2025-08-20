import pygame
from common import Button
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'client-network'))
from state import get_state

class SetupScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self.ready_button = Button(300, 500, 200, 50, "Sẵn sàng")

        # Grid
        self.grid_size = 10
        self.cell_size = 35
        self.grid_origin = (50, 100)

        # Predefined ships (simplified - just rectangles with colors)
        # Predefined ships (giờ dùng ảnh thay vì màu)
        self.ships_data = [
            {"length": 2, "image": "images/image1.png"},
            {"length": 3, "image": "images/image2.png"},
            {"length": 3, "image": "images/image3.png"},
            {"length": 4, "image": "images/image4.png"},
            {"length": 5, "image": "images/image5.png"},
        ]

        self.ships = []
        start_x = self.grid_origin[0] + self.grid_size * self.cell_size + 50
        start_y = 100
        gap = 15

        for idx, ship_data in enumerate(self.ships_data):
            length = ship_data["length"]
            img_path = ship_data["image"]
            # Load image
            raw_img = pygame.image.load(img_path).convert_alpha()
            # Scale theo chiều dài tàu (ngang)
            img = pygame.transform.scale(raw_img, (length * self.cell_size, self.cell_size))

            rect = img.get_rect()
            rect.topleft = (start_x, start_y + idx * (self.cell_size + gap))

            self.ships.append({
                "rect": rect,
                "length": length,
                "image": img,
                "placed": False,
                "grid_pos": None,
                "original_pos": (rect.x, rect.y)
            })

        # Dragging
        self.dragging_ship = None
        self.offset_x = 0
        self.offset_y = 0

        self.done = False
        self.next = None
        self.placed_ships = []
        
        self.ready_sent = False
        self.status_message = ""

    def handle_event(self, event):
        if self.ready_button.handle_event(event):
            if not self.ready_sent:
                placed_ships = []
                for ship in self.ships:
                    if ship["placed"]:
                        row, col = ship["grid_pos"]
                        placed_ships.append({
                            "length": ship["length"],
                            "pos": (row, col),   # (row, col)
                            "orientation": "H"         # hiện giờ chỉ ngang
                        })

                self.placed_ships = placed_ships   # <--- Lưu lại để BattleScreen dùng
                self.send_queue.put({
                    "action": "ready",
                    "name": self.username,
                    "ships": placed_ships
                })
                self.ready_sent = True
                self.status_message = "Đã gửi trạng thái sẵn sàng, đang chờ đối thủ..."

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for ship in self.ships:
                if ship["rect"].collidepoint(event.pos):
                    self.dragging_ship = ship
                    mx, my = event.pos
                    self.offset_x = ship["rect"].x - mx
                    self.offset_y = ship["rect"].y - my
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
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
                    # Check for overlaps with other placed ships
                    collision = False
                    for other_ship in self.ships:
                        if other_ship != self.dragging_ship and other_ship["placed"]:
                            other_row, other_col = other_ship["grid_pos"]
                            other_length = other_ship["length"]
                            # Check horizontal overlap
                            if row == other_row:
                                if not (col >= other_col + other_length or col + length <= other_col):
                                    collision = True
                                    break
                    
                    if not collision:
                        # Snap đúng vào grid
                        snap_x = self.grid_origin[0] + col * self.cell_size
                        snap_y = self.grid_origin[1] + row * self.cell_size
                        self.dragging_ship["rect"].topleft = (snap_x, snap_y)
                        self.dragging_ship["placed"] = True
                        self.dragging_ship["grid_pos"] = (row, col)  # góc trái trên
                    else:
                        # Return to original position if collision
                        self.dragging_ship["rect"].topleft = self.dragging_ship["original_pos"]
                        self.dragging_ship["placed"] = False
                        self.dragging_ship["grid_pos"] = None
                else:
                    # Return to original position if invalid placement
                    self.dragging_ship["rect"].topleft = self.dragging_ship["original_pos"]
                    self.dragging_ship["placed"] = False
                    self.dragging_ship["grid_pos"] = None

                self.dragging_ship = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_ship:
                mx, my = event.pos
                self.dragging_ship["rect"].x = mx + self.offset_x
                self.dragging_ship["rect"].y = my + self.offset_y

    def update(self):
        game_state = get_state()
        
        # Check if game has started
        if game_state.get_started():
            self.done = True
            self.next = "battle"
        
        # Update status based on players ready
        players = game_state.get_players()
        if len(players) < 2:
            self.status_message = "Đang chờ người chơi thứ hai..."
        elif self.ready_sent:
            self.status_message = "Đã sẵn sàng, đang chờ đối thủ..."

    def draw(self):
        self.screen.fill((30, 30, 60))

        # Title
        title = self.font.render(f"Bố trí tàu - {self.username}", True, (255, 255, 255))
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
                pygame.draw.rect(self.screen, (100, 150, 200), rect, 1)

        # Ships
        # Ships
        for ship in self.ships:
            self.screen.blit(ship["image"], ship["rect"].topleft)

        # Instructions
        instructions = [
            "Kéo thả tàu vào lưới",
            f"Đặt tất cả {len(self.ships)} tàu để sẵn sàng"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (450, 200 + i * 25))

        # Ready button (only enabled if all ships are placed)
        all_placed = all(ship["placed"] for ship in self.ships)
        if all_placed and not self.ready_sent:
            self.ready_button.color = (0, 150, 0)
            self.ready_button.text = "Sẵn sàng"
        elif self.ready_sent:
            self.ready_button.color = (100, 100, 100)
            self.ready_button.text = "Đã sẵn sàng"
        else:
            self.ready_button.color = (100, 100, 100)
            self.ready_button.text = "Đặt hết tàu"
        
        self.ready_button.draw(self.screen)

        # Status message
        if self.status_message:
            status_text = self.small_font.render(self.status_message, True, (255, 255, 0))
            status_rect = status_text.get_rect(center=(400, 570))
            self.screen.blit(status_text, status_rect)
        
        # Game state info
        game_state = get_state()
        players = game_state.get_players()
        if len(players) > 0:
            player_info = self.small_font.render(f"Người chơi: {', '.join(players)}", True, (150, 150, 150))
            self.screen.blit(player_info, (50, 60))

        pygame.display.flip()
