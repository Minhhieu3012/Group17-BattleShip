# Xử lý message từ client (join,place_ship,ready,shoot)
import uuid 
from utils import send_json, broadcast_room
from game_logic import Player 
from threading import Lock

rooms={} 
lock=Lock() # Khóa để đồng bộ hóa truy cập vào rooms

def handle_message(msg,player,room,conn):
    action=msg.get('action') # Lấy action từ message
    if action == 'join':
        return join_room(msg,conn)
    elif action == 'place_ship' and player and room: 
        x,y=msg['x'],msg['y'] # Lấy thông tin vị trí của tàu
        length,direction=msg['length'],msg['dir'] # Lấy thông tin chiều dài và hướng của tàu
        ok=player.board.place_ship(x,y,length,direction) # Đặt tàu trên board
        send_json(conn,{'action':'place_ship','ok':ok})
    elif action == 'ready' and player and room:
        player.ready = True
        if room.both_ready():
            room.started = True
            broadcast_room(room, {'action': 'start', 'turn': room.turn}) # Thông báo bắt đầu trò chơi
    elif action == 'shoot' and player and room and room.started: 
        handle_shoot(msg,player,room,conn)
    else:
        send_json(conn,{'action':'error','message':'Invalid action'}) 
    
    return player,room

def join_room(msg,conn):
    from game_logic import GameRoom # Nhập GameRoom tại đây để tránh lỗi vòng lặp nhập
    name=msg.get('name','Guest') # Lấy tên người chơi từ message
    room_id=msg.get('room_id') or str(uuid.uuid4()) # Lấy room_id từ message hoặc tạo mới
    with lock: # Sử dụng khóa để đồng bộ hóa truy cập vào rooms
        if room_id not in rooms:
            rooms[room_id]=GameRoom(room_id) # Tạo room mới nếu chưa có
        room=rooms[room_id] 

    player=Player(name,conn) # Tạo player mới
    if not room.add_player(player):
        send_json(conn,{'action':'error','message':'Room is full or does not exist'})
        return None,None
    send_json(conn,{'action':'join','room_id':room_id}) # Thông báo đã tham gia thành công
    broadcast_room(room,{'action':'player_list','players':[p.name for p in room.players]}) # Cập nhật danh sách người chơi
   
    return player,room

def handle_shoot(msg,player,room,conn):
    shooter_idx=room.players.index(player) # Lấy chỉ số của người chơi trong danh sách
    if shooter_idx != room.turn:
        send_json(conn,{'action':'error','message':'Not your turn'})
        return 
    target_idx=1-shooter_idx # Chỉ số của người chơi còn lại
    x,y=msg['x'],msg['y'] # Lấy tọa độ bắn từ message
    result=room.players[target_idx].board.receive_shot(x,y) # Nhận kết quả bắn từ board của người chơi còn lại
    broadcast_room(room,{'action':'shot_result','x':x,'y':y,'result':result,'by':player.name}) # Thông báo kết quả bắn
    if room.players[target_idx].board.check_all_sunk():
        broadcast_room(room,{'action':'game_over','winner':player.name})
        room.started=False
    else:
        room.turn = target_idx # Chuyển lượt cho người chơi còn lại