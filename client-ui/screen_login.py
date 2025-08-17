# screen_login.py
import pygame
from common import Button, InputBox

class LoginScreen:
    def __init__(self, screen, send_queue):
        self.screen = screen
        self.send_queue = send_queue
        self.font = pygame.font.SysFont("Arial", 32)

        self.input_box = InputBox(300, 250, 200, 40)
        self.start_button = Button(300, 320, 200, 50, "Start")

        self.done = False
        self.next = None
        self.username = ""

    def handle_event(self, event):
        self.input_box.handle_event(event)
        if self.start_button.handle_event(event):
            if self.input_box.text.strip():
                self.username = self.input_box.text.strip()
                self.send_queue.put({"action": "login", "name": self.username})
                self.done = True
                self.next = "lobby"

    def update(self):
        self.input_box.update()

    def draw(self):
        self.screen.fill((30, 30, 60))
        label = self.font.render("Enter your name:", True, (255, 255, 255))
        self.screen.blit(label, (280, 200))
        self.input_box.draw(self.screen)
        self.start_button.draw(self.screen)
        pygame.display.flip()
