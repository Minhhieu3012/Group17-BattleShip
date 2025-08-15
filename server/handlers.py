# Xử lý message từ client (join,place_ship,ready,shoot)
import uuid 
from utils import send_json, broadcast_room
from game_logic import Player 
from threading import Lock

room={} 
lock=Lock() # Khóa để đồng bộ hóa truy cập vào room

def handle_message(msg,player,room,conn):
    action=msg.get('action')
    if action == 'join':
        return join_room(msg,conn)
    elif action == 'place_ship' and player and room:
        x,y=msg['x'],msg['y']
        length,direction=msg['length'],msg['dir'] # Lấy thông tin vị trí, chiều dài và hướng của tàu
        ok=player.board.place_ship(x,y,length,direction)
        send_json(conn,{'action':'place_ship','ok':ok})
    elif action == 'ready' and player and room:
        player.ready = True
        if room.both_ready():
            room.started = True
            broadcast_room(room, {'action': 'start', 'turn': room.turn})
    elif action == 'shoot' and player and room and room.started:
        handle_shoot(msg,player,room,conn)
    else:
        send_json(conn,{'action':'error','message':'Invalid action'})
    
    return player,room


