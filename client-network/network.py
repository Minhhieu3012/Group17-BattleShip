# network.py — client mạng (JSON line) khớp handlers.py
# Server chấp nhận 4 action: join, place_ship, ready, shoot
import socket
import threading
import json
from queue import Queue, Empty
from typing import Optional, Dict, Any

from state import get_state

LINE_END = "\n"

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

    # ------------- lifecycle -------------
    def start(self, timeout: float = 5.0) -> bool:
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(timeout)
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(None)
            get_state().set_connected(True)
            _log(f"Connected to server at {self.host}:{self.port}")
        except Exception as e:
            get_state().set_connected(False)
            print("[ERROR] Could not connect to server:", e, flush=True)
            return False

        self._recv_thread = threading.Thread(target=self._recv_loop, name="recv_thread", daemon=True)
        self._send_thread = threading.Thread(target=self._send_loop, name="send_thread", daemon=True)
        self._recv_thread.start()
        self._send_thread.start()
        return True

    def stop(self):
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

    # ------------- receive -------------
    def _recv_loop(self):
        while not self._stop.is_set():
            try:
                data = self.sock.recv(4096)
                if not data:
                    _log("Server closed connection.")
                    get_state().set_connected(False)
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
            except Exception as e:
                if not self._stop.is_set():
                    print("[ERROR] recv_loop:", e, flush=True)
                    get_state().set_connected(False)
                    break

    def _handle_server_event(self, msg: Dict[str, Any]):
        act = msg.get("action")

        if act == "join":
            rid = msg.get("room_id")
            get_state().set_room(rid)
            get_state().set_joined(True)
            print(f"[SUCCESS] Tham gia phòng thành công. room_id={rid}", flush=True)
            return

        if act == "player_list":
            players = msg.get("players", [])
            get_state().set_players(players)
            print(f"[INFO] Người chơi trong phòng: {players}", flush=True)
            return

        if act == "start":
            get_state().set_started(True)
            get_state().set_turn(msg.get("turn"))
            get_state().set_game_phase("battle")
            print("[INFO] Trận đấu bắt đầu! Lượt của:", msg.get("turn"), flush=True)
            return

        if act == "place_ship":
            ok = msg.get("ok", False)
            if ok:
                print("[SUCCESS] Đặt tàu thành công!", flush=True)
            else:
                print("[ERROR] Không thể đặt tàu ở vị trí này!", flush=True)
            return

        if act == "shot_result":
            x, y = msg.get("x"), msg.get("y")
            result = msg.get("result")
            by = msg.get("by")
            get_state().add_shot_result(x, y, result, by)
            print(f"[SHOT] {by} bắn ({x},{y}) => {result}", flush=True)
            return

        if act == "turn_change":
            new_turn = msg.get("turn")
            get_state().set_turn(new_turn)
            print(f"[TURN] Chuyển lượt cho người chơi {new_turn}", flush=True)
            return

        if act == "game_over":
            winner = msg.get('winner')
            get_state().set_winner(winner)
            print(f"[GAME OVER] Người thắng: {winner}", flush=True)
            return

        if act == "opponent_left":
            print("[INFO] Đối thủ đã rời khỏi phòng", flush=True)
            get_state().set_opponent_left(True)
            return

        if act in ("error", "err"):
            error_msg = msg.get('message') or str(msg)
            get_state().set_last_error(error_msg)
            print(f"[FAIL] Lỗi từ server: {error_msg}", flush=True)
            return

        # else: just raw log
        print("[RECV]", msg, flush=True)

    # ------------- send -------------
    def _send_loop(self):
        while not self._stop.is_set():
            try:
                ui_msg = self.send_queue.get(timeout=0.2)
            except Empty:
                continue

            if not isinstance(ui_msg, dict):
                print("[WARN] Bỏ qua payload không phải dict:", ui_msg, flush=True)
                continue

            payload = self._translate_ui_action(ui_msg)
            if not payload:
                # e.g., login -> local only
                continue

            try:
                raw = json.dumps(payload, ensure_ascii=False) + LINE_END
                self.sock.sendall(raw.encode("utf-8"))
            except Exception as e:
                print("[ERROR] Failed to send payload:", e, flush=True)
                continue

            a = payload.get("action")
            if a == "join":
                rid = payload.get("room_id")
                if rid:
                    print(f"[INFO] Gửi yêu cầu vào phòng: {rid}", flush=True)
                else:
                    print("[INFO] Gửi yêu cầu tạo phòng mới (join không kèm room_id)", flush=True)
            elif a == "ready":
                print("[INFO] Gửi trạng thái sẵn sàng.", flush=True)
            elif a == "place_ship":
                print("[INFO] Gửi đặt tàu:", {k: payload.get(k) for k in ("x","y","length","dir")}, flush=True)
            elif a == "shoot":
                print("[INFO] Gửi lệnh bắn:", (payload.get("x"), payload.get("y")), flush=True)

    # ------------- translate UI -> server -------------
    def _translate_ui_action(self, ui_msg: Dict[str, Any]):
        """Chuẩn hoá payload UI thành 1 trong các action: join, place_ship, ready, shoot."""
        act = ui_msg.get("action")
        name = ui_msg.get("name") or ui_msg.get("username") or ui_msg.get("user")
        room_id = ui_msg.get("room_id") or ui_msg.get("room") or ui_msg.get("code")

        # Lưu tên local, không gửi action 'login' lên server (server không có 'login')
        if act in ("login", "signin"):
            if name:
                get_state().set_name(name)
                print(f"[INFO] Đăng nhập local: name={name} (không gửi server)", flush=True)
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
                except Exception:
                    pass
            return {"action": "place_ship", "x": x, "y": y, "length": length, "dir": direction}

        # Bắn
        if act in ("attack", "shoot", "fire"):
            x = ui_msg.get("x")
            y = ui_msg.get("y")
            pos = ui_msg.get("pos")
            if pos and (x is None or y is None):
                try:
                    y, x = int(pos[0]), int(pos[1])
                except Exception:
                    pass
            return {"action": "shoot", "x": x, "y": y}

        print("[WARN] Bỏ qua action UI không hỗ trợ:", act, ui_msg, flush=True)
        return None

# ---------- convenience API ----------
_client_singleton: Optional[NetworkClient] = None

def start_network(send_queue: Queue, host: str = "127.0.0.1", port: int = 8000) -> NetworkClient:
    client = NetworkClient(host, port, send_queue)
    if client.start():
        global _client_singleton
        _client_singleton = client
    return client

def get_state_proxy():
    return get_state()
