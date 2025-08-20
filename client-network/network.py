# network.py — client 
import socket
import threading
import json
import time
from queue import Queue, Empty
from typing import Optional, Dict, Any

from state import get_state

LINE_END = "\n"
RECONNECT_DELAY = 3.0  # seconds
MAX_RECONNECT_ATTEMPTS = 5

def _log(*args):
    print("[NET]", *args, flush=True)

class NetworkClient:
    """TCP client gửi/nhận JSON theo dòng và CHUYỂN action UI -> action server."""
    def __init__(self, host: str, port: int, send_queue: Queue):
        self.host = host
        self.port = port
        self.send_queue = send_queue
        self.sock: Optional[socket.socket] = None
        self._stop = threading.Event()
        self._recv_thread: Optional[threading.Thread] = None
        self._send_thread: Optional[threading.Thread] = None
        self._buffer = ""
        self._reconnect_attempts = 0
        self._last_connection_time = 0

    # ------------- lifecycle -------------
    def start(self, timeout: float = 5.0) -> bool:
        return self._connect(timeout)

    def _connect(self, timeout: float = 5.0) -> bool:
        """Attempt to connect to server"""
        try:
            if self.sock:
                self.sock.close()
            
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(timeout)
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(None)
            
            get_state().set_connected(True)
            self._reconnect_attempts = 0
            self._last_connection_time = time.time()
            _log(f"Connected to server at {self.host}:{self.port}")
            
            # Start threads if not already running
            if not self._recv_thread or not self._recv_thread.is_alive():
                self._recv_thread = threading.Thread(target=self._recv_loop, name="recv_thread", daemon=True)
                self._recv_thread.start()
                
            if not self._send_thread or not self._send_thread.is_alive():
                self._send_thread = threading.Thread(target=self._send_loop, name="send_thread", daemon=True)
                self._send_thread.start()
                
            return True
        except Exception as e:
            error_msg = f"Không thể kết nối tới server: {e}"
            get_state().set_connected(False, error_msg)
            _log(f"Connection failed: {e}")
            return False

    def _attempt_reconnect(self):
        """Attempt to reconnect to server"""
        if self._stop.is_set() or self._reconnect_attempts >= MAX_RECONNECT_ATTEMPTS:
            return False
            
        self._reconnect_attempts += 1
        _log(f"Attempting to reconnect... ({self._reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS})")
        
        time.sleep(RECONNECT_DELAY)
        
        if self._connect():
            _log("Reconnection successful!")
            # Re-login if we have a username
            name = get_state().get_name()
            if name:
                self.send_queue.put({"action": "login", "name": name})
            return True
        return False

    def stop(self):
        _log("Stopping network client...")
        self._stop.set()
        try:
            if self.sock:
                self.sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        get_state().set_connected(False)

    # ------------- receive -------------
    def _recv_loop(self):
        while not self._stop.is_set():
            try:
                if not self.sock:
                    time.sleep(0.1)
                    continue
                    
                data = self.sock.recv(4096)
                if not data:
                    _log("Server closed connection.")
                    get_state().set_connected(False, "Server đã đóng kết nối")
                    
                    # Attempt reconnection
                    if not self._stop.is_set():
                        if self._attempt_reconnect():
                            continue
                        else:
                            _log("Failed to reconnect after maximum attempts")
                    break
                    
                self._buffer += data.decode("utf-8", errors="ignore")
                while "\n" in self._buffer:
                    line, self._buffer = self._buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        print("[WARN] Received non-JSON line:", line, flush=True)
                        continue

                    get_state().buffered_messages.put(msg)
                    self._handle_server_event(msg)
                    
            except socket.timeout:
                continue
            except Exception as e:
                if not self._stop.is_set():
                    _log(f"recv_loop error: {e}")
                    get_state().set_connected(False, str(e))
                    
                    # Attempt reconnection
                    if self._attempt_reconnect():
                        continue
                    else:
                        break

    def _handle_server_event(self, msg: Dict[str, Any]):
        """Handle incoming messages from server with improved error handling"""
        act = msg.get("action")

        if act == "join":
            rid = msg.get("room_id")
            get_state().set_room(rid)
            get_state().set_joined(True)
            _log(f"Joined room successfully. room_id={rid}")
            return

        if act == "player_list":
            players = msg.get("players", [])
            get_state().set_players(players)
            _log(f"Players in room: {players}")
            return

        if act == "start":
            get_state().set_started(True)
            get_state().set_turn(msg.get("turn"))
            get_state().set_game_phase("battle")
            _log(f"Game started! Turn: {msg.get('turn')}")
            return

        if act == "ready":
            status = msg.get("status")
            if status == "confirmed":
                get_state().set_success_message("Đã sẵn sàng!")
                _log("Ready status confirmed")
            return

        if act == "place_ship":
            ok = msg.get("ok", False)
            if ok:
                get_state().set_success_message("Đặt tàu thành công!")
                _log("Ship placed successfully!")
            else:
                get_state().set_last_error("Không thể đặt tàu ở vị trí này!")
                _log("Failed to place ship at this position!")
            return

        if act == "shot_result":
            x, y = msg.get("x"), msg.get("y")
            result = msg.get("result")
            by = msg.get("by")
            get_state().add_shot_result(x, y, result, by)
            _log(f"Shot result: {by} shot ({x},{y}) => {result}")
            return

        if act == "turn_change":
            new_turn = msg.get("turn")
            get_state().set_turn(new_turn)
            _log(f"Turn changed to player {new_turn}")
            return

        if act == "game_over":
            winner = msg.get('winner')
            get_state().set_winner(winner)
            _log(f"Game Over! Winner: {winner}")
            return

        if act == "opponent_left":
            _log("Opponent left the game")
            get_state().set_opponent_left(True)
            return

        if act in ("error", "err"):
            error_msg = msg.get('message') or str(msg)
            get_state().set_last_error(error_msg)
            _log(f"Server error: {error_msg}")
            
            # Handle specific error types
            if "full" in error_msg.lower():
                get_state().set_last_error("Phòng đã đầy!")
            elif "not exist" in error_msg.lower() or "not found" in error_msg.lower():
                get_state().set_last_error("Phòng không tồn tại!")
            elif "not your turn" in error_msg.lower():
                get_state().set_last_error("Chưa đến lượt của bạn!")
            return

        # Unknown message type - just log it
        _log(f"Unknown message: {msg}")

    # ------------- send -------------
    def _send_loop(self):
        while not self._stop.is_set():
            try:
                ui_msg = self.send_queue.get(timeout=0.2)
            except Empty:
                continue

            if not isinstance(ui_msg, dict):
                print("[WARN] Ignoring non-dict payload:", ui_msg, flush=True)
                continue

            # Check connection before sending
            if not get_state().get_connected():
                _log("Cannot send message: not connected to server")
                get_state().set_last_error("Không có kết nối tới server")
                continue

            payload = self._translate_ui_action(ui_msg)
            if not payload:
                # e.g., login -> local only
                continue

            try:
                raw = json.dumps(payload, ensure_ascii=False) + LINE_END
                if self.sock:
                    self.sock.sendall(raw.encode("utf-8"))
                else:
                    _log("No socket available for sending")
                    continue
            except Exception as e:
                _log(f"Failed to send payload: {e}")
                get_state().set_connected(False, f"Lỗi gửi dữ liệu: {e}")
                # Try to reconnect
                if not self._stop.is_set():
                    self._attempt_reconnect()
                continue

            # Log successful sends
            action = payload.get("action")
            if action == "join":
                room_id = payload.get("room_id")
                if room_id:
                    _log(f"Requested to join room: {room_id}")
                else:
                    _log("Requested to create new room")
            elif action == "ready":
                _log("Sent ready status")
            elif action == "place_ship":
                _log(f"Sent place ship: {payload.get('x')}, {payload.get('y')}")
            elif action == "shoot":
                _log(f"Sent shoot command: ({payload.get('x')}, {payload.get('y')})")

    # ------------- translate UI -> server -------------
    def _translate_ui_action(self, ui_msg: Dict[str, Any]):
        """Chuẩn hóa payload UI thành 1 trong các action: join, place_ship, ready, shoot."""
        act = ui_msg.get("action")
        name = ui_msg.get("name") or ui_msg.get("username") or ui_msg.get("user")
        room_id = ui_msg.get("room_id") or ui_msg.get("room") or ui_msg.get("code")

        # Lưu tên local, không gửi action 'login' lên server
        if act in ("login", "signin"):
            if name:
                get_state().set_name(name)
                get_state().set_success_message(f"Đăng nhập với tên: {name}")
                _log(f"Local login: name={name} ")
            return None

        # Tạo/Tham gia phòng -> 'join'
        if act in ("create_room", "join_room", "join"):
            payload = {"action": "join"}
            if name:
                payload["name"] = name
            if room_id:
                payload["room_id"] = str(room_id)
            return payload

        # Sẵn sàng
        if act == "ready":
            payload = {"action": "ready"}
            ships = ui_msg.get("ships", [])
            if ships:
                payload["ships"] = ships
            return payload

        # Đặt tàu
        if act in ("place_ship", "place"):
            x = ui_msg.get("x")
            y = ui_msg.get("y")
            length = ui_msg.get("length") or ui_msg.get("len") or ui_msg.get("size")
            direction = ui_msg.get("dir") or ui_msg.get("direction") or ui_msg.get("orient") or ui_msg.get("orientation")
            pos = ui_msg.get("pos")
            
            if pos and (x is None or y is None):
                try:
                    y, x = int(pos[0]), int(pos[1])  # row, col -> y, x
                except (IndexError, ValueError, TypeError):
                    _log(f"Invalid position format: {pos}")
                    
            return {"action": "place_ship", "x": x, "y": y, "length": length, "dir": direction}

        # Bắn
        if act in ("attack", "shoot", "fire"):
            x = ui_msg.get("x")
            y = ui_msg.get("y")
            pos = ui_msg.get("pos")
            
            if pos and (x is None or y is None):
                try:
                    y, x = int(pos[0]), int(pos[1])
                except (IndexError, ValueError, TypeError):
                    _log(f"Invalid position format: {pos}")
                    
            return {"action": "shoot", "x": x, "y": y}

        _log(f"Unsupported UI action: {act}")
        get_state().set_last_error(f"Hành động không được hỗ trợ: {act}")
        return None

    # ------------- Status methods -------------
    def is_connected(self) -> bool:
        """Check if client is connected to server"""
        return get_state().get_connected()

    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for debugging"""
        return {
            "connected": self.is_connected(),
            "host": self.host,
            "port": self.port,
            "reconnect_attempts": self._reconnect_attempts,
            "last_connection_time": self._last_connection_time
        }

# ---------- convenience API ----------
_client_singleton: Optional[NetworkClient] = None

def start_network(send_queue: Queue, host: str = "127.0.0.1", port: int = 8000) -> NetworkClient:
    """Start network client and return instance"""
    global _client_singleton
    
    # Stop existing client if any
    if _client_singleton:
        _client_singleton.stop()
    
    client = NetworkClient(host, port, send_queue)
    if client.start():
        _client_singleton = client
        _log(f"Network client started successfully")
    else:
        _log(f"Failed to start network client")
    
    return client

def get_network_client() -> Optional[NetworkClient]:
    """Get current network client instance"""
    return _client_singleton

def get_state_proxy():
    """Get game state proxy"""
    return get_state()

def stop_network():
    """Stop current network client"""
    global _client_singleton
    if _client_singleton:
        _client_singleton.stop()
        _client_singleton = None