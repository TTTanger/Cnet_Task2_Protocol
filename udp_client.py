import socket
import threading
from lossy_channel import lossy
from protocol import Frame

class client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.c.bind((self.host, self.port))
        self.c.settimeout(1.0)  # Set the timeout to 1 second
        self.seq_num = 0    # Message sequence number set to 0
        self.expected_seq = 0   # The expected sequence number set to 0
        print("Client started on ", self.host, ":", self.port)

    def send(self, message, server):
        max_retries = 3
        retries = 0

        while retries < max_retries:
            try:
                frame = Frame.create_frame(self.seq_num, message)
                lossy_frame = lossy(frame)
                self.c.sendto(lossy_frame, server)
                print(f"Sent frame with seq={self.seq_num}")
                try:
                    ack_frame, addr = self.c.recvfrom(1024)
                    ack_seq, ack_data = Frame.check_frame(ack_frame)
                    
                    if ack_data == b'ACK' and ack_seq == self.seq_num:
                        print(f"Received ACK for seq={self.seq_num}")
                        self.seq_num = 1 - self.seq_num  # 切换序列号(0/1)
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
            frame, addr = self.c.recvfrom(1024)
            seq_num, decode_data = Frame.check_frame(frame)
            if seq_num is None:
                print(f"Frame check failed: {decode_data}")
                return
            print(f"Received message", decode_data.decode("ascii"), "from", addr, "with seq={seq_num}")
            ack = Frame.create_frame(seq_num, b'ACK')
            self.c.sendto(ack, addr)

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
        server = ('127.0.0.1', 65433)
        while True:
            message = input("Enter message: ").encode('ascii')
            self.send(message, server)
    
    def receive_thread(self):
        while True:
            self.receive()

if __name__ == "__main__":
    c = client('127.0.0.1', 65432)
    
    # Create and start threads
    send_thread = threading.Thread(target=c.send_thread)
    receive_thread = threading.Thread(target=c.receive_thread)
    
    send_thread.start()
    receive_thread.start()
