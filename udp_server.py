import socket               
import threading

from lossy_channel import lossy
from protocol import Frame

TIMEOUT = 1.0  # 1s, ACK timeout for retransmission
MAX_RETRY = 5

class server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.host, self.port))
        self.s.settimeout(1.0)  
        self.seq_num = 0  
        self.expected_seq = 0 
        print("Server started on ", self.host, ":", self.port)

    def send(self, message, client):
        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                frame = Frame.create_frame(self.seq_num, message)
                lossy_frame = lossy(frame)
                self.s.sendto(lossy_frame, client)
                print(f"Sent frame with seq={self.seq_num}")
                try:
                    ack_frame, addr = self.s.recvfrom(1024)
                    ack_seq, ack_data = Frame.check_frame(ack_frame)
                    
                    if ack_data == b'ACK' and ack_seq == self.seq_num:
                        print(f"Received ACK for seq={self.seq_num}")
                        self.seq_num = 1 - self.seq_num 
                        return True
                        
                except socket.timeout:
                    print(f"Timeout, retrying... ({retries + 1})")
                    retries += 1
                    continue
                    
            except Exception as e:
                print(f"Error: {e}")
                retries += 1

        print("Max retries reached!")
        return False
    
    def receive(self):
        try:
            frame, addr = self.s.recvfrom(1024)
            seq_num, decode_data = Frame.check_frame(frame)
            if seq_num is None:
                print(f"Frame check failed: {decode_data}")
                return
            print(f"Received message", decode_data.decode("ascii"), "from", addr, "with seq={seq_num}")
            ack = Frame.create_frame(seq_num, b'ACK')
            self.s.sendto(ack, addr)

            if seq_num == self.expected_seq:
                print(f"Message: {decode_data.decode('ascii')} from {addr}")
                self.expected_seq = 1 - self.expected_seq
            else:
                print(f"Duplicate message with seq={seq_num}")

        except socket.timeout:
            # Without printing, skip
            pass
        except Exception as e:
            print(f"Error in receive: {e}")
    
    def send_thread(self):
        client = ('127.0.0.1', 65432)
        while True:
            message = input("Enter message: ").encode('ascii')
            self.send(message, client)
    
    def receive_thread(self):
        while True:
            self.receive()

if __name__ == "__main__":
    s = server('127.0.0.1', 65433)
    
    # Create and start threads
    send_thread = threading.Thread(target=s.send_thread)
    receive_thread = threading.Thread(target=s.receive_thread)
    
    send_thread.start()
    receive_thread.start()