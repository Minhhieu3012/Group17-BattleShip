# Board, Player, GameRoom (logic core)
class Board:
    # Hàm khởi tạo 
    def __init__(self,size=10): # 10x10
        self.size=size 
        self.grid=[['~']*size for _ in range(size)] # tạo ma trận 2D, (~): biển
        self.ships=[] # Mỗi tàu được lưu như một list các tọa độ (x,y)
        self.hits=set() # Tập hợp các tọa độ đã bắn
    
    # Hàm đặt tàu 
    # x: cột, y: hàng, length: độ dài tàu, direction: 'H' (ngang) hoặc 'V' (dọc)
    def place_ship(self, x, y, length, direction):
        if direction == 'H':
            return self._place_ship_horizontal(x, y, length)
        else:
            return self._place_ship_vertical(x, y, length)

    def _place_ship_horizontal(self, x, y, length):
        if x + length > self.size:
            return False
        if any(self.grid[y][x + i] != '~' for i in range(length)):
            return False
        for i in range(length):
            self.grid[y][x + i] = 'S'
        self.ships.append([(x + i, y) for i in range(length)])
        return True

    def _place_ship_vertical(self, x, y, length):
        if y + length > self.size:
            return False
        if any(self.grid[y + i][x] != '~' for i in range(length)):
            return False
        for i in range(length):
            self.grid[y + i][x] = 'S'
        self.ships.append([(x, y + i) for i in range(length)])
        return True

    # Hàm nhận shot từ người chơi
    def receive_shot(self,x,y):
        if(x,y) in self.hits: # Đã bắn vào tọa độ này rồi
            return 'repeat'
        self.hits.add((x,y)) # Đánh dấu tọa độ đã bắn
        if self.grid[y][x] == 'S':
            self.grid[y][x] = 'X' # Đánh dấu trúng tàu
            if self._is_ship_sunk(x,y):
                return 'sunk'
            return 'hit' # Trúng tàu nhưng chưa chìm
        else:
            self.grid[y][x] = 'O' # Đánh dấu trúng biển
            return 'miss'

    # Hàm kiểm tra xem tàu có bị chìm không
    def _is_ship_sunk(self,x,y):
        for ship in self.ships: # Duyệt qua từng tàu
            if(x,y) in ship:  # Nếu tọa độ bắn trúng tàu
                return all(self.grid[sy][sx] == 'X' for sx,sy in ship) # Kiểm tra xem tất cả các phần của tàu đã bị đánh chìm chưa
        return False
    
    def check_all_sunk(self):
        return all(all(self.grid[sy][sx] == 'X' for sx,sy in ship) for ship in self.ships)
    
class Player:
    def __init__(self,name,conn):
        self.name=name 
        self.conn=conn # Kết nối mạng
        self.board=Board() # Mỗi người chơi có một board riêng
        self.ready=False # Trạng thái sẵn sàng


class GameRoom:
    def __init__(self,room_id):
        self.room_id=room_id
        self.players=[] # Danh sách người chơi trong phòng
        self.turn=0
        self.started=False # Trạng thái trò chơi
    
    def add_player(self,player):
        if len(self.players) < 2:
            self.players.append(player)
            return True
        return False # Không thể thêm người chơi

    def both_ready(self):
        return len(self.players) == 2 and all(p.ready for p in self.players) # Kiểm tra xem cả hai người chơi đã sẵn sàng chưa