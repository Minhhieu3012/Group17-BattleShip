import pygame
from queue import Queue
from screen_login import LoginScreen
from screen_lobby import LobbyScreen
from screen_setup import SetupScreen
from screen_battle import BattleScreen
from screen_create_room import CreateRoomScreen
from screen_join_room import JoinRoomScreen

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("BattleShip")
clock = pygame.time.Clock()

send_queue = Queue()

# Màn hình đầu tiên là Login
current_screen = LoginScreen(screen, send_queue)

running = True
username = None  # khởi tạo biến username

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

        elif current_screen.next == "create_room":
            current_screen = CreateRoomScreen(screen, send_queue, username)

        elif current_screen.next == "join_room":
            current_screen = JoinRoomScreen(screen, send_queue, username)

        elif current_screen.next == "setup":
            current_screen = SetupScreen(screen, send_queue, username)

        elif current_screen.next == "battle":
            current_screen = BattleScreen(
        screen, send_queue, username, current_screen.placed_ships
    )


    clock.tick(30)

pygame.quit()
