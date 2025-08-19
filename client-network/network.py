# network.py
import socket
import threading
import json
from queue import Queue

class NetworkClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        # Queue để main_thread gửi dữ liệu cho network_thread
        self.send_queue = Queue()
        # Queue để network_thread gửi dữ liệu nhận được cho main_thread
        self.recv_queue = Queue()

    def connect(self):
        """Khởi tạo kết nối và các luồng gửi/nhận."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            
            # Bắt đầu luồng nhận dữ liệu từ server
            self.recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.recv_thread.start()

            # Bắt đầu luồng gửi dữ liệu tới server
            self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
            self.send_thread.start()
            
            print("Connected to server.")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Đóng kết nối."""
        if self.connected:
            self.connected = False
            self.sock.close()
            print("Disconnected from server.")

    def _receive_loop(self):
        """
        Luồng này (recv_thread) liên tục lắng nghe dữ liệu từ server.
        Dữ liệu được parse theo dòng và đưa vào recv_queue.
        """
        buffer = ""
        while self.connected:
            try:
                data = self.sock.recv(1024).decode('utf-8')
                if not data:
                    # Server đã đóng kết nối
                    self.recv_queue.put({"action": "server_disconnect"})
                    break
                
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        msg = json.loads(line)
                        self.recv_queue.put(msg)
            except (ConnectionResetError, BrokenPipeError):
                self.recv_queue.put({"action": "server_disconnect"})
                break
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e} in line: '{line}'")
            except Exception as e:
                print(f"Receive loop error: {e}")
                break
        self.disconnect()

    def _send_loop(self):
        """
        Luồng này lấy các message từ send_queue và gửi chúng tới server.
        """
        while self.connected:
            try:
                data_to_send = self.send_queue.get() # Lấy message từ queue (blocking)
                if data_to_send is None: # Tín hiệu để dừng
                    break
                
                json_data = json.dumps(data_to_send) + "\n"
                self.sock.sendall(json_data.encode('utf-8'))
            except Exception as e:
                print(f"Send loop error: {e}")
                break
        self.disconnect()