from utils.hamming import hamming74_encode, hamming74_decode
from utils.crc import calc_crc

# Define the frame
class Frame:
    """Create the frame from string data"""
    @staticmethod
    def create_frame(seq_num, data):
        # Add sequence number (1 byte)
        seq_byte = seq_num.to_bytes(1, byteorder='big')

        # Encode data with Hamming74
        encoded_blocks = []
        for i in range(0, len(data), 4):
            block = data[i:i+4]
            encoded, _ = hamming74_encode(block)
            encoded_blocks.append(encoded)
        data_with_hamming = b''.join(encoded_blocks)

        # Define the original length
        original_len = len(data).to_bytes(1, byteorder='big')

        # Calculate CRC
        crc = calc_crc(seq_byte + data_with_hamming + original_len, 0x8005)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        
        # Return combined frame as bytes
        return seq_byte + data_with_hamming + original_len + crc_bytes
    
    @staticmethod
    def check_frame(frame):
        try:
            # Extract seq_num, data and crc
            seq_num = frame[0]
            data_with_hamming = frame[1:-3]
            original_len = int.from_bytes(frame[-3:-2], byteorder='big')
            received_crc = int.from_bytes(frame[-2:], byteorder='big')

            # Decode data with Hamming74
            decoded = bytearray()
            bytes_needed = original_len
            for i in range(0, len(data_with_hamming), 7):
                block = data_with_hamming[i:i+7]
                # Decode each block
                group_len = min(4, bytes_needed - len(decoded))
                decoded_block = hamming74_decode(block, group_len)
                decoded.extend(decoded_block)
                if len(decoded) >= bytes_needed:
                    break
            decode_data = bytes(decoded[:original_len])

            # Recompose the frame for CRC calculation
            seq_byte = seq_num.to_bytes(1, byteorder='big')
            original_len_byte = original_len.to_bytes(1, byteorder='big')
            frame_for_crc = seq_byte + data_with_hamming + original_len_byte

            # Calculate CRC
            calculated_crc = calc_crc(frame_for_crc, 0x8005)

            # Compare calculated CRC with received CRC
            if calculated_crc == received_crc:
                return seq_num, decode_data
            else:
                return None, b'CRC error'
                
        except Exception as e:
            return None, f'Frame check error: {str(e)}'.encode()
    
# Test
if __name__ == "__main__":
    data = b'Hello world!'
    frame = Frame.create_frame(1, data)
    print(f"Frame: {frame.hex()}")
    print(f"Data part: {frame[:-3].hex()}")
    print(f"Length part: {frame[-3:-2].hex()}")
    print(f"CRC part: {frame[-2:].hex()}")
    print(f"Decoded data: {Frame.check_frame(frame)}")

