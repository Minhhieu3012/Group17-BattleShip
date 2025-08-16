# Chạy server, khởi tạo socket, nhận kết nối 
import socket 
import threading 
import json 
from handlers import handle_message,rooms,lock
from utils import broadcast_room

def handle_client(conn,addr):
    player=None
    room=None
    try:
        buffer=""
        while True:
            data=conn.recv(1024)
            if not data:
                break 
            buffer+=data.decode('utf-8')
            while "\n" in buffer:
                line,buffer=buffer.split("\n",1) # Tách từng dòng message
                try:
                    msg=json.loads(line) # Chuyển đổi JSON thành dict
                except:
                    continue
                player,room=handle_message(msg,player,room,conn)
    except:
        pass
    finally:
        if player and room:
            with lock: # Sử dụng khóa để đồng bộ hóa truy cập vào rooms
                if player in room.players:
                    room.players.remove(player)
                if len(room.players)==0:
                    rooms.pop(room.room_id, None) # Xóa room nếu không còn người chơi
            broadcast_room(room,{"action":"opponent_left"}) # Thông báo người chơi đã rời khỏi phòng
        conn.close() # Đóng kết nối
