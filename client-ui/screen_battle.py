import pygame
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'client-network'))
from state import get_state

class BattleScreen:
    def __init__(self, screen, send_queue, username, my_ships):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.my_ships = my_ships   # ✅ danh sách tàu lấy từ SetupScreen
        self.font = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)

        # Grid của mình
        self.my_grid_size = 10
        self.cell_size = 30
        self.my_origin = (80, 120)
        # Grid của đối thủ
        self.enemy_origin = (450, 120)
        
        # Track shots
        self.my_shots = {}  # (x, y) -> result
        self.enemy_shots = {}  # (x, y) -> result

        self.done = False
        self.next = None
        self.winner = None # None = chưa xong, "me" = mình thắng, "enemy" = thua
        self.turn_info = ""

        # Button rects (để dễ xử lý click khi game over)
        self.play_again_btn = pygame.Rect(220, 380, 160, 50)
        self.exit_btn = pygame.Rect(440, 380, 120, 50)

    def handle_event(self, event):
        if self.winner is not None:
            # Game over -> chỉ xử lý nút
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if self.play_again_btn.collidepoint(mx, my):
                    print("Chơi tiếp")
                    self.done = True
                    self.next = "lobby"   # Quay về lobby
                elif self.exit_btn.collidepoint(mx, my):
                    print("Thoát game")
                    pygame.quit()
                    exit()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Click vào lưới đối thủ để bắn
            mx, my = event.pos
            col = (mx - self.enemy_origin[0]) // self.cell_size
            row = (my - self.enemy_origin[1]) // self.cell_size
            
            if 0 <= col < self.my_grid_size and 0 <= row < self.my_grid_size:
                # Check if it's our turn and we haven't shot this position
                game_state = get_state()
                players = game_state.get_players()
                my_turn = False
                
                if len(players) >= 2:
                    my_index = 0 if players[0] == self.username else 1
                    current_turn = game_state.get_turn()
                    my_turn = (current_turn == my_index)
                
                if my_turn and (col, row) not in self.my_shots:
                    # Gửi nước đi tới server
                    self.send_queue.put({
                        "action": "shoot",
                        "x": col,
                        "y": row
                    })
                    print(f"{self.username} bắn vào ({col}, {row})")

    def update(self):
        game_state = get_state()
        
        # Update shot results
        shot_results = game_state.get_shot_results()
        for shot in shot_results:
            x, y, result, by = shot["x"], shot["y"], shot["result"], shot["by"]
            if by == self.username:
                self.my_shots[(x, y)] = result
            else:
                self.enemy_shots[(x, y)] = result
        
        # Clear processed shots
        if shot_results:
            game_state.clear_shot_results()
        
        # Update turn info
        players = game_state.get_players()
        current_turn = game_state.get_turn()
        if len(players) >= 2 and current_turn is not None:
            if current_turn == 0:
                turn_player = players[0]
            else:
                turn_player = players[1]
            
            if turn_player == self.username:
                self.turn_info = "Lượt của bạn - Click vào lưới đối thủ để bắn"
            else:
                self.turn_info = f"Lượt của {turn_player} - Đang chờ..."
        
        # Check for game over
        winner = game_state.get_winner()
        if winner and not self.winner:
            if winner == self.username:
                self.winner = "me"
            else:
                self.winner = "enemy"

    def draw(self):
        self.screen.fill((20, 40, 70))

        title = self.font.render(f"Trận chiến - {self.username}", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 30))
        self.screen.blit(title, title_rect)

        # Turn info
        if self.turn_info and not self.winner:
            turn_color = (0, 255, 0) if "của bạn" in self.turn_info else (255, 255, 0)
            turn_text = self.small_font.render(self.turn_info, True, turn_color)
            turn_rect = turn_text.get_rect(center=(400, 60))
            self.screen.blit(turn_text, turn_rect)

        # Labels
        my_label = self.font.render("Lưới của bạn", True, (200, 200, 200))
        enemy_label = self.font.render("Lưới đối thủ", True, (200, 200, 200))
        self.screen.blit(my_label, (self.my_origin[0], 80))
        self.screen.blit(enemy_label, (self.enemy_origin[0], 80))

        # Vẽ lưới mình
        self._draw_my_grid()
        
        # Vẽ lưới đối thủ
        self._draw_enemy_grid()

        # Khi game kết thúc -> vẽ overlay + nút
        if self.winner is not None:
            self._draw_game_over()

        # 🔑 luôn luôn flip ở cuối
        pygame.display.flip()

    def _draw_my_grid(self):
        # Draw grid
        for row in range(self.my_grid_size):
            for col in range(self.my_grid_size):
                rect = pygame.Rect(
                    self.my_origin[0] + col * self.cell_size,
                    self.my_origin[1] + row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(self.screen, (0, 150, 255), rect, 1)
        
        # Draw ships
        for ship in self.my_ships:
            row, col = ship["pos"]
            length = ship["length"]
            for i in range(length):
                rect = pygame.Rect(
                    self.my_origin[0] + (col + i) * self.cell_size,
                    self.my_origin[1] + row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(self.screen, (100, 200, 100), rect)  # xanh lá cho tàu
                pygame.draw.rect(self.screen, (0, 100, 0), rect, 2)   # viền
        
        # Draw enemy shots on my grid
        for (col, row), result in self.enemy_shots.items():
            rect = pygame.Rect(
                self.my_origin[0] + col * self.cell_size,
                self.my_origin[1] + row * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            if result in ['hit', 'sunk']:
                pygame.draw.rect(self.screen, (255, 0, 0), rect)  # Red for hits
            else:
                pygame.draw.rect(self.screen, (100, 100, 100), rect)  # Gray for misses

    def _draw_enemy_grid(self):
        # Draw grid
        for row in range(self.my_grid_size):
            for col in range(self.my_grid_size):
                rect = pygame.Rect(
                    self.enemy_origin[0] + col * self.cell_size,
                    self.enemy_origin[1] + row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(self.screen, (255, 100, 100), rect, 1)
        
        # Draw my shots on enemy grid
        for (col, row), result in self.my_shots.items():
            rect = pygame.Rect(
                self.enemy_origin[0] + col * self.cell_size,
                self.enemy_origin[1] + row * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            if result in ['hit', 'sunk']:
                pygame.draw.rect(self.screen, (255, 0, 0), rect)  # Red for hits
                if result == 'sunk':
                    # Draw X for sunk ships
                    pygame.draw.line(self.screen, (255, 255, 255), 
                                   (rect.left, rect.top), (rect.right, rect.bottom), 3)
                    pygame.draw.line(self.screen, (255, 255, 255), 
                                   (rect.right, rect.top), (rect.left, rect.bottom), 3)
            elif result == 'miss':
                pygame.draw.circle(self.screen, (100, 100, 100), rect.center, 8)  # Circle for miss

    def _draw_game_over(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.winner == "me":
            msg = self.big_font.render("BẠN THẮNG!", True, (0, 255, 0))
        else:
            msg = self.big_font.render("BẠN THUA!", True, (255, 50, 50))

        msg_rect = msg.get_rect(center=(self.screen.get_width()//2, 300))
        self.screen.blit(msg, msg_rect)

        pygame.draw.rect(self.screen, (0, 200, 0), self.play_again_btn)
        play_text = self.font.render("Chơi lại", True, (255, 255, 255))
        play_rect = play_text.get_rect(center=self.play_again_btn.center)
        self.screen.blit(play_text, play_rect)

        pygame.draw.rect(self.screen, (200, 0, 0), self.exit_btn)
        exit_text = self.font.render("Thoát", True, (255, 255, 255))
        exit_rect = exit_text.get_rect(center=self.exit_btn.center)
        self.screen.blit(exit_text, exit_rect)

    def set_winner(self, winner: str):
        """winner = 'me' hoặc 'enemy'"""
        self.winner = winner
        print("Game Over! Winner:", "Bạn" if winner == "me" else "Đối thủ")
