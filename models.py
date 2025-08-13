class Player:
    def __init__(self,name,sock,addr):
        self.name=name 
        self.sock=sock 
        self.addr=addr
        self.board=[["~"]*10 for _ in range(10)] # ~: biển 
        self.ships=[] # [(x,y,length,shape,dir)]
        self.shot_received=set()

class GameRoom:
    def __init__(self,room_id):
        self.room_id=room_id
        self.players=[]
        self.state='waiting' # waiting,placing,playing,finished
        self.turn=0
        self.lock=None # threading.lock() gán sau 