import pygame

class BattleScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 28)
        self.big_font = pygame.font.SysFont("Arial", 48, bold=True)

        # Grid của mình
        self.my_grid_size = 10
        self.cell_size = 30
        self.my_origin = (80, 120)

        # Grid của đối thủ
        self.enemy_origin = (450, 120)

        self.done = False
        self.next = None
        self.winner = "me"  # None = chưa xong, "me" = mình thắng, "enemy" = thua

        # Button rects (để dễ xử lý click)
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
                    self.next = "setup"   # hoặc màn hình chọn lại
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
                # Gửi nước đi tới server
                self.send_queue.put({
                    "action": "attack",
                    "user": self.username,
                    "pos": (row, col)
                })
                print(f"{self.username} bắn vào ({row}, {col})")

    def update(self):
        pass

    def draw(self):
        self.screen.fill((20, 40, 70))

        title = self.font.render(f"Battle Phase - {self.username}", True, (255, 255, 255))
        self.screen.blit(title, (260, 30))

        # Label
        my_label = self.font.render("Your Grid", True, (200, 200, 200))
        enemy_label = self.font.render("Enemy Grid", True, (200, 200, 200))
        self.screen.blit(my_label, (self.my_origin[0], 80))
        self.screen.blit(enemy_label, (self.enemy_origin[0], 80))

        # Vẽ lưới mình
        for row in range(self.my_grid_size):
            for col in range(self.my_grid_size):
                rect = pygame.Rect(
                    self.my_origin[0] + col * self.cell_size,
                    self.my_origin[1] + row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(self.screen, (0, 150, 255), rect, 1)

        # Vẽ lưới đối thủ
        for row in range(self.my_grid_size):
            for col in range(self.my_grid_size):
                rect = pygame.Rect(
                    self.enemy_origin[0] + col * self.cell_size,
                    self.enemy_origin[1] + row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(self.screen, (255, 100, 100), rect, 1)
        # Khi game kết thúc -> vẽ nút
        if self.winner is not None:
            # Tạo lớp phủ bán trong suốt
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # RGBA: màu đen, alpha=180/255 -> hơi trong suốt
            self.screen.blit(overlay, (0, 0))

            # Thông báo kết quả
            if self.winner == "me":
                msg = self.big_font.render("YOU WIN!", True, (0, 255, 0))
            else:
                msg = self.big_font.render("YOU LOSE!", True, (255, 50, 50))

            # canh giữa
            msg_rect = msg.get_rect(center=(self.screen.get_width()//2, 300))
            self.screen.blit(msg, msg_rect)

            # Vẽ nút Play Again
            pygame.draw.rect(self.screen, (0, 200, 0), self.play_again_btn)
            play_text = self.font.render("Play Again", True, (255, 255, 255))
            play_rect = play_text.get_rect(center=self.play_again_btn.center)
            self.screen.blit(play_text, play_rect)

            # Vẽ nút Exit
            pygame.draw.rect(self.screen, (200, 0, 0), self.exit_btn)
            exit_text = self.font.render("Exit", True, (255, 255, 255))
            exit_rect = exit_text.get_rect(center=self.exit_btn.center)
            self.screen.blit(exit_text, exit_rect)


            pygame.display.flip()

    def set_winner(self, winner: str):
        """winner = 'me' hoặc 'enemy'"""
        self.winner = winner
        print("Game Over! Winner:", "Bạn" if winner == "me" else "Đối thủ")
