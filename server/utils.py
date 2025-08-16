# Hàm hỗ trợ: gửi JSON, broadcast
import json 

# Hàm gửi dữ liệu JSON qua kết nối
def send_json(conn,data):
    try:
        conn.sendall((json.dumps(data)+"\n").encode('utf-8')) # Chuyển đổi dữ liệu thành JSON và gửi
    except Exception as e:
        print(f"Error sending JSON: {e}")

# Hàm broadcast dữ liệu đến tất cả người chơi trong phòng
def broadcast_room(room,data):
    for p in room.players: 
        send_json(p.conn,data)