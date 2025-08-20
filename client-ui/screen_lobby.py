import pygame
from common import Button
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'client-network'))
from state import get_state

class LobbyScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self.create_button = Button(250, 250, 300, 50, "Tạo phòng")
        self.join_button = Button(250, 320, 300, 50, "Tham gia phòng")

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
        # Check if we've joined a room automatically
        game_state = get_state()
        if game_state.get_joined():
            self.done = True
            self.next = "setup"

    def draw(self):
        self.screen.fill((50, 50, 100))
        
        title = self.font.render(f"Chào mừng, {self.username}", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 150))
        self.screen.blit(title, title_rect)

        self.create_button.draw(self.screen)
        self.join_button.draw(self.screen)
        
        # Show connection status
        game_state = get_state()
        if game_state.get_connected():
            status = self.small_font.render("Đã kết nối tới server", True, (0, 255, 0))
        else:
            status = self.small_font.render("Mất kết nối tới server", True, (255, 0, 0))
        
        status_rect = status.get_rect(center=(400, 500))
        self.screen.blit(status, status_rect)

        pygame.display.flip()