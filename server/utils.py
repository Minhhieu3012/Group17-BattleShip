# Hàm hỗ trợ: gửi JSON, broadcast
import json 

def send_json(conn,data):
    try:
        conn.sendall((json.dumps(data)+"\n").encode('utf-8'))
    except:
        pass

def broadcast_room(room,data):
    for p in room.players:
        send_json(p.conn,data)