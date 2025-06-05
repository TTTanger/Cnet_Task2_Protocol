import socket
import threading as t
import protocol
from lossy_channel import lossy
from utils.hamming import fix_hamming74
from utils.crc import verify_crc
class server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        print(f"Server started on {host}:{port}")

    def send_packet(self, server_socket):
        while True:
            try:
                data = input("Enter data to send: ")
                
                # Create frame with CRC
                frame = protocol.Frame.create_frame(data)
                frame_bytes = frame.to_bytes()
                
                if frame_bytes is None:
                    print("Failed to create frame")
                    continue
                    
                # Apply lossy channel
                msg = lossy(frame_bytes)
                
                self.socket.sendto(msg, server_socket)
                print(f"Sent frame with Data: {format(frame.data_with_hamming,'04X')}, CRC: {format(frame.crc, '04X')}\n")
                
            except Exception as e:
                print(f"Error in send_packet: {e}\n")
                continue

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
                if verify_crc(frame.data_with_hamming, frame.crc):
                    print(f"Valid frame received:")
                    print(f"Data: {format(frame.data_with_hamming,'04X')}")
                    print(f"CRC: {format(frame.crc, '04X')}\n")
                    fixed_data = fix_hamming74(frame.data_with_hamming)
                    
                    # Check errors and fix them
                    fixed_data, positions, had_errors = fix_hamming74(frame.data_with_hamming)
                    if had_errors:
                        print(f"Errors detected and fixed at positions: {positions}")
                        print(f"Fixed data: {format(fixed_data,'04X')}\n")
                else:
                    print(f"Corrupted frame received\n")
                    
            except Exception as e:
                print(f"Error in receive_packet: {e}\n")
                continue

if __name__ == "__main__":
    server = server("127.0.0.1", 65433)
    client_addr = ("127.0.0.1", 65432)
    t1 = t.Thread(target=server.send_packet, args=(client_addr,))
    t2 = t.Thread(target=server.receive_packet)
    t1.start()
    t2.start()