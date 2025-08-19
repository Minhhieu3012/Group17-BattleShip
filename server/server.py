# Chạy server, khởi tạo socket, nhận kết nối 
import socket 
import threading 
import json 
from handlers import handle_message, rooms, lock
from utils import broadcast_room

def handle_client(conn, addr):
    player = None
    room = None
    try:
        buffer = ""  # Buffer để lưu dữ liệu nhận được
        while True:
            data = conn.recv(1024)  # Nhận dữ liệu từ client qua socket
            if not data:
                break 
            buffer += data.decode('utf-8')  # Thêm dữ liệu vào buffer
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)  # Tách từng dòng message
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)  # Chuyển đổi JSON thành dict
                except json.JSONDecodeError:
                    continue
                player, room = handle_message(msg, player, room, conn)  # Xử lý message từ client
    except Exception as e:
        print(f"[ERROR] Client {addr} error: {e}")
    finally:
        if player and room:
            with lock:  # Sử dụng khóa để đồng bộ hóa truy cập vào rooms
                if player in room.players:
                    room.players.remove(player)
                if len(room.players) == 0:
                    rooms.pop(room.room_id, None)  # Xóa room nếu không còn người chơi
            broadcast_room(room, {"action": "opponent_left"})  # Thông báo người chơi đã rời khỏi phòng
        conn.close()  # Đóng kết nối

def start_server(host='0.0.0.0', port=8000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    print(f"Battleship Server running on {host}:{port}")
    try:
        while True:
            conn, addr = s.accept()
            print(f"[INFO] New client connected: {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()  # Mỗi kết nối sẽ chạy trên một thread riêng
    except KeyboardInterrupt:
        print("\n[INFO] Server shutting down...")
    finally:
        s.close()

if __name__ == "__main__":
    start_server()
