# state.py — trạng thái chia sẻ giữa network và UI
import threading
from queue import Queue
from typing import List, Dict, Any, Optional

class GameState:
    """Thread-safe game/network state shared with the UI."""
    def __init__(self):
        self._lock = threading.RLock()
        # kết nối & danh tính
        self.connected = False
        self.name = None
        self.connection_error = None
        
        # phòng & trận
        self.room_id = None
        self.joined = False
        self.players = []
        self.started = False
        self.turn = None  # 0/1
        self.ready_count = 0  # số người đã ready
        
        # game state
        self.game_phase = "login"  # login, lobby, setup, battle, ended
        self.winner = None
        self.opponent_left = False
        self.last_error = None
        self.error_timestamp = 0
        
        # shot results for battle screen
        self.shot_results = []
        
        # UI feedback
        self.status_message = ""
        self.success_message = ""
        
        # mailbox cho UI
        self.buffered_messages = Queue()

    # --- Connection management ---
    def set_connected(self, value: bool, error: str = None):
        with self._lock:
            self.connected = value
            if not value:
                self.connection_error = error or "Mất kết nối"
                # Reset game state when disconnected
                self.reset_game_state()
            else:
                self.connection_error = None

    def set_name(self, name: str):
        with self._lock:
            self.name = name

    def get_connected(self):
        with self._lock:
            return self.connected

    def get_connection_error(self):
        with self._lock:
            return self.connection_error

    def get_name(self):
        with self._lock:
            return self.name

    # --- Room management ---
    def set_room(self, room_id):
        with self._lock:
            self.room_id = room_id

    def set_joined(self, value: bool):
        with self._lock:
            self.joined = value
            if value:
                self.game_phase = "setup"
                self.success_message = "Tham gia phòng thành công!"

    def set_players(self, players: List[str]):
        with self._lock:
            old_count = len(self.players)
            self.players = list(players) if players else []
            new_count = len(self.players)
            
            # Update status message based on player count
            if new_count == 1:
                self.status_message = "Đang chờ người chơi khác..."
            elif new_count == 2:
                self.status_message = "Đã đủ người chơi!"
            
            # Detect if someone left
            if old_count > new_count and old_count > 0:
                self.status_message = "Có người rời phòng"

    def get_room_id(self):
        with self._lock:
            return self.room_id

    def get_joined(self):
        with self._lock:
            return self.joined

    def get_players(self):
        with self._lock:
            return self.players[:]

    # --- Game state management ---
    def set_started(self, v: bool):
        with self._lock:
            self.started = v
            if v:
                self.game_phase = "battle"
                self.success_message = "Trận đấu bắt đầu!"

    def set_turn(self, t):
        with self._lock:
            self.turn = t

    def set_game_phase(self, phase: str):
        with self._lock:
            old_phase = self.game_phase
            self.game_phase = phase
            
            # Update status based on phase change
            if phase == "battle" and old_phase != "battle":
                self.status_message = "Chuẩn bị chiến đấu!"
            elif phase == "ended":
                self.status_message = "Trận đấu kết thúc"

    def set_winner(self, winner: str):
        with self._lock:
            self.winner = winner
            self.game_phase = "ended"
            if winner:
                self.success_message = f"Người thắng: {winner}"

    def set_opponent_left(self, left: bool):
        with self._lock:
            self.opponent_left = left
            if left:
                self.status_message = "Đối thủ đã rời game"
                self.game_phase = "lobby"

    def set_ready_count(self, count: int):
        with self._lock:
            self.ready_count = count

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

    def get_ready_count(self):
        with self._lock:
            return self.ready_count

    # --- Error & Message handling ---
    def set_last_error(self, error: str):
        with self._lock:
            self.last_error = error
            self.error_timestamp = threading.get_ident()  # Simple timestamp
            
            # Clear success message when error occurs
            self.success_message = ""

    def get_last_error(self):
        with self._lock:
            error = self.last_error
            self.last_error = None  # Clear after reading
            return error

    def set_status_message(self, message: str):
        with self._lock:
            self.status_message = message

    def get_status_message(self):
        with self._lock:
            return self.status_message

    def set_success_message(self, message: str):
        with self._lock:
            self.success_message = message

    def get_success_message(self):
        with self._lock:
            message = self.success_message
            self.success_message = ""  # Clear after reading
            return message

    # --- Shot results for battle ---
    def add_shot_result(self, x, y, result, by):
        with self._lock:
            self.shot_results.append({
                "x": x, "y": y, "result": result, "by": by
            })

    def get_shot_results(self):
        with self._lock:
            return self.shot_results[:]

    def clear_shot_results(self):
        with self._lock:
            self.shot_results.clear()

    # --- Utility methods ---
    def reset_game_state(self):
        """Reset game-specific state (keep connection info)"""
        with self._lock:
            self.room_id = None
            self.joined = False
            self.players = []
            self.started = False
            self.turn = None
            self.ready_count = 0
            self.winner = None
            self.opponent_left = False
            self.shot_results.clear()
            self.game_phase = "lobby" if self.connected else "login"
            self.status_message = ""

    def is_my_turn(self, username: str) -> bool:
        """Check if it's the given player's turn"""
        with self._lock:
            if not self.started or self.turn is None or len(self.players) < 2:
                return False
            
            try:
                player_index = self.players.index(username)
                return player_index == self.turn
            except ValueError:
                return False

    def get_opponent_name(self, my_name: str) -> Optional[str]:
        """Get opponent's name"""
        with self._lock:
            if len(self.players) != 2:
                return None
            
            for player in self.players:
                if player != my_name:
                    return player
            return None

    # --- Debug helpers ---
    def get_debug_info(self) -> Dict[str, Any]:
        """Get current state for debugging"""
        with self._lock:
            return {
                "connected": self.connected,
                "name": self.name,
                "room_id": self.room_id,
                "joined": self.joined,
                "players": self.players,
                "started": self.started,
                "turn": self.turn,
                "game_phase": self.game_phase,
                "winner": self.winner,
                "shot_results_count": len(self.shot_results),
                "buffered_messages_count": self.buffered_messages.qsize()
            }

# Singleton-like accessor
_game_state = GameState()

def get_state() -> GameState:
    return _game_state

def reset_state():
    """Reset to initial state (for testing or restart)"""
    global _game_state
    _game_state = GameState()