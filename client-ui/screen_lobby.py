import pygame
from common import Button

class LobbyScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 32)

        self.create_button = Button(250, 250, 300, 50, "Create Room")
        self.join_button = Button(250, 320, 300, 50, "Join Room")

        self.done = False
        self.next = None
        self.data = {}

    def handle_event(self, event):
        if self.create_button.handle_event(event):
            # chuyển sang màn hình tạo phòng
            self.done = True
            self.next = "create_room"
            self.data = {"username": self.username}

        if self.join_button.handle_event(event):
            # chuyển sang màn hình join room
            self.done = True
            self.next = "join_room"
            self.data = {"username": self.username}

    def update(self):
        pass

    def draw(self):
        self.screen.fill((50, 50, 100))
        title = self.font.render(f"Welcome, {self.username}", True, (255, 255, 255))
        self.screen.blit(title, (250, 150))

        self.create_button.draw(self.screen)
        self.join_button.draw(self.screen)

        pygame.display.flip()
