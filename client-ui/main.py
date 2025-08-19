# main.py — tích hợp với client-network/network.py (chuẩn actions: join, place_ship, ready, shoot)
import os
import sys
from pathlib import Path
import pygame
from queue import Queue

# ----- Thêm đường dẫn tới thư mục 'client-network' (có dấu '-') -----
BASE = Path(__file__).resolve().parent                     # .../client-ui
NET_DIR = BASE.parent / "client-network"                   # .../client-network
if NET_DIR.exists():
    sys.path.append(str(NET_DIR))
else:
    print("[FATAL] Không tìm thấy thư mục 'client-network' cạnh 'client-ui'.")
    raise SystemExit(1)

# Import module mạng chuẩn (network.py)
from network import start_network, get_state_proxy

# ----- Import các màn hình UI -----
from screen_login import LoginScreen
from screen_lobby import LobbyScreen
from screen_setup import SetupScreen
from screen_battle import BattleScreen
from screen_create_room import CreateRoomScreen
from screen_join_room import JoinRoomScreen

# ----- Khởi tạo Pygame -----
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("BattleShip")
clock = pygame.time.Clock()

# ----- Networking -----
send_queue = Queue()

# Cho phép đổi nhanh host/port bằng biến môi trường
NET_HOST = os.environ.get("BS_HOST", "127.0.0.1")
NET_PORT = int(os.environ.get("BS_PORT", "5000"))
_client = start_network(send_queue, host=NET_HOST, port=NET_PORT)

# (tuỳ chọn) Lấy state mạng nếu UI cần
_game_state = get_state_proxy()

# ----- State machine chuyển màn hình -----
running = True
username = ""
current_screen = LoginScreen(screen, send_queue)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            if hasattr(current_screen, "handle_event"):
                current_screen.handle_event(event)

    if hasattr(current_screen, "update"):
        current_screen.update()
    if hasattr(current_screen, "draw"):
        current_screen.draw()

    if getattr(current_screen, "done", False):
        nxt = getattr(current_screen, "next", None)

        # Lấy username từ màn hình login khi chuyển sang lobby
        if isinstance(current_screen, LoginScreen):
            username = getattr(current_screen, "username", "") or username

        if nxt == "lobby":
            current_screen = LobbyScreen(screen, send_queue, username)
        elif nxt == "create_room":
            current_screen = CreateRoomScreen(screen, send_queue, username)
        elif nxt == "join_room":
            current_screen = JoinRoomScreen(screen, send_queue, username)
        elif nxt == "setup":
            current_screen = SetupScreen(screen, send_queue, username)
        elif nxt == "battle":
            current_screen = BattleScreen(screen, send_queue, username)
        else:
            current_screen = LobbyScreen(screen, send_queue, username) if username else LoginScreen(screen, send_queue)

    clock.tick(60)

pygame.quit()
