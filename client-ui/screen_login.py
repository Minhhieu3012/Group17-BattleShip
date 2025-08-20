# screen_login.py
import pygame
from common import Button, InputBox
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'client-network'))
from state import get_state

class LoginScreen:
    def __init__(self, screen, send_queue):
        self.screen = screen
        self.send_queue = send_queue
        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self.input_box = InputBox(300, 250, 200, 40)
        self.start_button = Button(300, 320, 200, 50, "Start")

        self.done = False
        self.next = None
        self.username = ""
        self.connection_status = ""

    def handle_event(self, event):
        result = self.input_box.handle_event(event)
        if result:  # Enter pressed
            if self.input_box.text.strip():
                self._start_game()
        
        if self.start_button.handle_event(event):
            if self.input_box.text.strip():
                self._start_game()

    def _start_game(self):
        self.username = self.input_box.text.strip()
        self.send_queue.put({"action": "login", "name": self.username})
        self.done = True
        self.next = "lobby"

    def update(self):
        self.input_box.update()
        
        # Update connection status
        game_state = get_state()
        if game_state.get_connected():
            self.connection_status = "Kết nối thành công"
        else:
            self.connection_status = "Đang kết nối tới server..."

    def draw(self):
        self.screen.fill((30, 30, 60))
        
        title = pygame.font.SysFont("Arial", 48).render("BATTLESHIP", True, (255, 215, 0))
        title_rect = title.get_rect(center=(400, 100))
        self.screen.blit(title, title_rect)
        
        label = self.font.render("Nhập tên của bạn:", True, (255, 255, 255))
        self.screen.blit(label, (280, 200))
        
        self.input_box.draw(self.screen)
        self.start_button.draw(self.screen)
        
        # Connection status
        status_color = (0, 255, 0) if "thành công" in self.connection_status else (255, 255, 0)
        status_text = self.small_font.render(self.connection_status, True, status_color)
        status_rect = status_text.get_rect(center=(400, 450))
        self.screen.blit(status_text, status_rect)
        
        pygame.display.flip()