# Board, Player, GameRoom (logic core)

class Board:
    def __init__(self,size=10):
        self.size=size
        self.grid=[['~']*size for _ in range(size)]
        self.ships=[]
        self.hits=set()
    
    def place_ship(self,x,y,length,direction):
        if direction=='H':
            if x + length > self.size:
                return False
            for i in range(length):
                if self.grid[y][x+i] != '~':
                    return False
            for i in range(length):
                self.grid[y][x+i] = 'S'
            self.ships.append([(x+i,y) for i in range(length)])
        else:
            if y + length > self.size:
                return False
            for i in range(length):
                if self.grid[y+i][x] != '~':
                    return False
            for i in range(length):
                self.grid[y+i][x] = 'S'
            self.ships.append([(x,y+i) for i in range(length)])
        return True

    def receive_shot(self,x,y):
        if(x,y) in self.hits:
            return 'repeat'
        self.hits.add((x,y))
        if self.grid[y][x] == 'S':
            self.grid[y][x] = 'X'
            if self._is_ship_sunk(x,y):
                return 'sunk'
            return 'hit'
        else:
            self.grid[y][x] = 'O'
            return 'miss'
    
    def _is_ship_sunk(self,x,y):
        for ship in self.ships:
            if(x,y) in ship: 
                return all(self.grid[sy][sx] == 'X' for sx,sy in ship)
        return False
    
    def check_all_sunk(self):
        return all(all(self.grid[sy][sx] == 'X' for sx,sy in ship) for ship in self.ships)
