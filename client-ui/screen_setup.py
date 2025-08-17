import pygame
from common import Button

class SetupScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 28)

        self.ready_button = Button(300, 500, 200, 50, "Ready")

        # Demo: chưa có logic đặt tàu, tạm cho 1 grid
        self.grid_size = 10
        self.cell_size = 40
        self.grid_origin = (100, 100)

        self.done = False
        self.next = None

    def handle_event(self, event):
        if self.ready_button.handle_event(event):
            # Khi nhấn Ready thì gửi thông điệp lên server
            self.send_queue.put({"action": "ready", "user": self.username})
            self.done = True
            self.next = "battle"

    def update(self):
        pass

    def draw(self):
        self.screen.fill((30, 30, 60))

        # Tiêu đề
        title = self.font.render(f"Setup Ships - {self.username}", True, (255, 255, 255))
        self.screen.blit(title, (250, 30))

        # Vẽ grid 10x10
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                rect = pygame.Rect(
                    self.grid_origin[0] + col * self.cell_size,
                    self.grid_origin[1] + row * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

        # Vẽ nút Ready
        self.ready_button.draw(self.screen)

        pygame.display.flip()
