# game_state.py

class GameState:
    """Lưu trữ toàn bộ trạng thái của game phía client."""
    def __init__(self):
        self.username = ""
        self.room_id = None
        self.players_in_room = []
        
        # Trạng thái game
        self.game_phase = "login" # login, lobby, setup, battle, game_over
        self.is_my_turn = False
        self.message = "Welcome to BattleShip!" # Hiển thị thông báo trạng thái
        
        # Dữ liệu bảng
        self.my_board = [['~'] * 10 for _ in range(10)]
        self.enemy_board = [['~'] * 10 for _ in range(10)] # Bảng của đối thủ, ban đầu là biển
        
        # Kết quả trận đấu
        self.winner = None
        self.opponent_left = False

    def update_from_server(self, msg):
        """
        Cập nhật trạng thái game dựa trên message từ server.
        Đây là trái tim của việc chuyển đổi dữ liệu mạng thành UI state.
        """
        action = msg.get('action')

        if action == 'join':
            self.room_id = msg.get('room_id')
            self.message = f"Joined Room: {self.room_id}"
        
        elif action == 'player_list':
            self.players_in_room = msg.get('players', [])

        elif action == 'start':
            self.game_phase = "battle"
            # Giả sử server trả về tên người đi trước
            turn_player = msg.get('turn_player_name') # Cần server gửi `turn_player_name`
            self.is_my_turn = (self.username == turn_player)
            self.message = f"Game started! Turn: {turn_player}"

        elif action == 'shot_result':
            x, y = msg['x'], msg['y']
            result = msg['result']
            shooter = msg['by']
            
            # Cập nhật bảng tương ứng
            if shooter == self.username:
                # Mình bắn, cập nhật bảng đối thủ
                if result in ['hit', 'sunk']:
                    self.enemy_board[y][x] = 'X' # Trúng
                else: # miss, repeat
                    self.enemy_board[y][x] = 'O' # Trượt
            else:
                # Đối thủ bắn, cập nhật bảng của mình
                if result in ['hit', 'sunk']:
                    self.my_board[y][x] = 'X' # Bị bắn trúng
                else:
                    self.my_board[y][x] = 'O' # Bị bắn trượt
            
            # Chuyển lượt
            if result != 'hit': # Theo luật "bắn trúng được bắn tiếp"
                self.is_my_turn = not self.is_my_turn
            
            self.message = f"{shooter} shot at ({x},{y}): {result}. Your turn: {self.is_my_turn}"

        elif action == 'game_over':
            self.game_phase = "game_over"
            self.winner = msg.get('winner')
            self.message = f"Game Over! Winner is {self.winner}"

        elif action == 'opponent_left':
            self.opponent_left = True
            self.game_phase = "game_over"
            self.message = "Opponent has disconnected. You win!"

        elif action == 'error':
            self.message = f"Error: {msg.get('message')}"