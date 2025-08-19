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
        # game state
        self.game_phase = "login"  # login, lobby, setup, battle, ended
        self.winner = None
        self.opponent_left = False
        self.last_error = None
        # shot results for battle screen
        self.shot_results = []
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

    def set_game_phase(self, phase: str):
        with self._lock:
            self.game_phase = phase

    def set_winner(self, winner: str):
        with self._lock:
            self.winner = winner

    def set_opponent_left(self, left: bool):
        with self._lock:
            self.opponent_left = left

    def set_last_error(self, error: str):
        with self._lock:
            self.last_error = error

    def add_shot_result(self, x, y, result, by):
        with self._lock:
            self.shot_results.append({
                "x": x, "y": y, "result": result, "by": by
            })

    # --- getters an toàn luồng ---
    def get_connected(self):
        with self._lock:
            return self.connected

    def get_name(self):
        with self._lock:
            return self.name

    def get_room_id(self):
        with self._lock:
            return self.room_id

    def get_joined(self):
        with self._lock:
            return self.joined

    def get_players(self):
        with self._lock:
            return self.players[:]

    def get_started(self):
        with self._lock:
            return self.started

    def get_turn(self):
        with self._lock:
            return self.turn

    def get_game_phase(self):
        with self._lock:
            return self.game_phase

    def get_winner(self):
        with self._lock:
            return self.winner

    def get_opponent_left(self):
        with self._lock:
            return self.opponent_left

    def get_last_error(self):
        with self._lock:
            error = self.last_error
            self.last_error = None  # Clear after reading
            return error

    def get_shot_results(self):
        with self._lock:
            return self.shot_results[:]

    def clear_shot_results(self):
        with self._lock:
            self.shot_results.clear()

# Singleton-like accessor
_game_state = GameState()

def get_state() -> GameState:
    return _game_state
