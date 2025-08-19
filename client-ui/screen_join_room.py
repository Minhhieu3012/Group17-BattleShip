import pygame
from common import Button
from common import InputBox

class JoinRoomScreen:
    def __init__(self, screen, send_queue, username):
        self.screen = screen
        self.send_queue = send_queue
        self.username = username
        self.font = pygame.font.SysFont("Arial", 32)

        self.input_box = InputBox(250, 270, 300, 50)
        self.back_button = Button(250, 350, 300, 50, "Join")

        self.done = False
        self.next = None

    def handle_event(self, event):
        code = self.input_box.handle_event(event)
        if code is not None:
            self._join_room(code)

        if self.back_button.handle_event(event):
            if self.input_box.text.strip():
                self._join_room(self.input_box.text.strip())

    def _join_room(self, code):
        self.send_queue.put({"action": "join_room", "user": self.username, "room": code})
        self.done = True
        self.next = "setup"

    def update(self):
        pass

    def draw(self):
        self.screen.fill((50, 50, 100))
        msg = self.font.render("Enter Room Code:", True, (255, 255, 255))
        self.screen.blit(msg, (250, 220))
        self.input_box.draw(self.screen)
        self.back_button.draw(self.screen)
        pygame.display.flip()
