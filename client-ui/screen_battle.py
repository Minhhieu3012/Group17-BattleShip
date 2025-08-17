import pygame

class BattleScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 28)

        # Grid của mình
        self.my_grid_size = 10
        self.cell_size = 30
        self.my_origin = (80, 120)

        # Grid của đối thủ
        self.enemy_origin = (450, 120)

        self.done = False
        self.next = None

    def handle_event(self, event):
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

        pygame.display.flip()
