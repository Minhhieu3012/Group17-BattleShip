import pygame
from common import Button
import random
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'client-network'))
from state import get_state

class CreateRoomScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self.room_code = str(random.randint(1000, 9999))
        self.send_queue.put({"action": "create_room", "name": self.username, "room_id": self.room_code})

        self.continue_button = Button(250, 400, 300, 50, "Tiếp tục")
        self.back_button = Button(250, 470, 300, 50, "Quay lại")

        self.done = False
        self.next = None
        self.waiting_for_player = True

    def handle_event(self, event):
        if self.continue_button.handle_event(event):
            self.done = True
            self.next = "setup"
            
        if self.back_button.handle_event(event):
            self.done = True
            self.next = "lobby"

    def update(self):
        game_state = get_state()
        players = game_state.get_players()
        if len(players) >= 2:
            self.waiting_for_player = False

    def draw(self):
        self.screen.fill((50, 50, 100))
        
        title = self.font.render("Phòng đã được tạo!", True, (255, 255, 0))
        title_rect = title.get_rect(center=(400, 200))
        self.screen.blit(title, title_rect)
        
        code_text = self.font.render(f"Mã phòng: {self.room_code}", True, (255, 255, 255))
        code_rect = code_text.get_rect(center=(400, 250))
        self.screen.blit(code_text, code_rect)
        
        game_state = get_state()
        players = game_state.get_players()
        player_text = self.small_font.render(f"Người chơi: {len(players)}/2", True, (200, 200, 200))
        player_rect = player_text.get_rect(center=(400, 300))
        self.screen.blit(player_text, player_rect)
        
        if self.waiting_for_player:
            waiting_text = self.small_font.render("Đang chờ người chơi khác...", True, (255, 255, 0))
            waiting_rect = waiting_text.get_rect(center=(400, 350))
            self.screen.blit(waiting_text, waiting_rect)
        
        self.continue_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        pygame.display.flip()