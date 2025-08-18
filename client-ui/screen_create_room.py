import pygame
from common import Button
import random

class CreateRoomScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 32)

        self.room_code = str(random.randint(1000, 9999))
        self.send_queue.put({"action": "create_room", "user": self.username, "room": self.room_code})

        self.back_button = Button(250, 400, 300, 50, "Continue")

        self.done = False
        self.next = None

    def handle_event(self, event):
        if self.back_button.handle_event(event):
            self.done = True
            self.next = "setup"

    def update(self):
        pass

    def draw(self):
        self.screen.fill((50, 50, 100))
        msg = self.font.render(f"Room Created! Code: {self.room_code}", True, (255, 255, 0))
        self.screen.blit(msg, (200, 250))
        self.back_button.draw(self.screen)
        pygame.display.flip()
