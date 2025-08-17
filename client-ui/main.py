import pygame
from queue import Queue
from screen_login import LoginScreen
from screen_lobby import LobbyScreen
from screen_setup import SetupScreen
from screen_battle import BattleScreen   # thêm vào

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("BattleShip")
clock = pygame.time.Clock()

send_queue = Queue()

current_screen = LoginScreen(screen, send_queue)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        current_screen.handle_event(event)

    current_screen.update()
    current_screen.draw()

    # Logic chuyển màn hình
    if current_screen.done:
        if current_screen.next == "lobby":
            username = current_screen.username
            current_screen = LobbyScreen(screen, send_queue, username)

        elif current_screen.next == "setup":
            username = current_screen.username
            current_screen = SetupScreen(screen, send_queue, username)

        elif current_screen.next == "battle":
            username = current_screen.username
            current_screen = BattleScreen(screen, send_queue, username)

    clock.tick(30)

pygame.quit()
