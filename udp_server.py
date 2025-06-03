import socket
import threading as t
import random
from lossy_channel import lossy
import protocol

class server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        print(f"Server started on {host}:{port}")

    def receive_packet(self):
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                
                # Reconstruct frame from received bytes
                frame = protocol.Frame.from_bytes(data)
                if frame is None:
                    print("Failed to reconstruct frame")
                    continue
                    
                print(f"Received from {addr}")
                
                # Verify CRC
                if frame.verify_crc():
                    print(f"Valid frame received:")
                    print(f"Data: {frame.data}")
                    print(f"Sequence: {frame.seq_num}")
                    print(f"CRC: {format(frame.crc, '04X')}\n")
                else:
                    print(f"Corrupted frame received\n")
                    
            except Exception as e:
                print(f"Error in receive_packet: {e}\n")
                continue

    def send_packet(self, server_socket):
        while True:
            try:
                # Generate random sequence number
                seq_num = random.randint(0, 255)
                data = input("Enter data to send: ")
                
                # Create frame with CRC
                frame = protocol.Frame.create_frame(data, seq_num)
                frame_bytes = frame.to_bytes()
                
                if frame_bytes is None:
                    print("Failed to create frame")
                    continue
                    
                # Apply lossy channel
                msg = lossy(frame_bytes)
                
                self.socket.sendto(msg, server_socket)
                print(f"Sent frame with seq_num: {seq_num}, CRC: {format(frame.crc, '04X')}\n")
                
            except Exception as e:
                print(f"Error in send_packet: {e}\n")
                continue

if __name__ == "__main__":
    server = server("127.0.0.1", 65433)
    client_addr = ("127.0.0.1", 65432)
    t1 = t.Thread(target=server.send_packet, args=(client_addr,))
    t2 = t.Thread(target=server.receive_packet)
    t1.start()
    t2.start()