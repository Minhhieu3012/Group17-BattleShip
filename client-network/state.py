# state.py — trạng thái chia sẻ giữa network và UI
import threading
from queue import Queue

class GameState:
    """Thread-safe game/network state shared with the UI."""
    def __init__(self):
        self._lock = threading.RLock()
        # kết nối & danh tính
        self.connected = False
        self.name = None
        # phòng & trận
        self.room_id = None
        self.joined = False
        self.players = []
        self.started = False
        self.turn = None  # 0/1
        # mailbox cho UI
        self.buffered_messages = Queue()

    # --- setters an toàn luồng ---
    def set_connected(self, value: bool):
        with self._lock:
            self.connected = value

    def set_name(self, name: str):
        with self._lock:
            self.name = name

    def set_room(self, room_id):
        with self._lock:
            self.room_id = room_id

    def set_joined(self, value: bool):
        with self._lock:
            self.joined = value

    def set_players(self, arr):
        with self._lock:
            self.players = list(arr) if arr else []

    def set_started(self, v: bool):
        with self._lock:
            self.started = v

    def set_turn(self, t):
        with self._lock:
            self.turn = t

# Singleton-like accessor
_game_state = GameState()

def get_state() -> GameState:
    return _game_state
