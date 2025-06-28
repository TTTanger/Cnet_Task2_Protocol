from utils.hamming import hamming74_encode, hamming74_decode
from utils.crc import calc_crc

# Define the frame
class Frame:
    """Create the frame from string data"""
    # Fragment size constant (bytes)
    FRAGMENT_SIZE = 16

    @staticmethod
    def create_frame(seq_num, data, fragment_id=0, total_fragments=1):
        # Add sequence number (1 byte)
        seq_byte = seq_num.to_bytes(1, byteorder='big')

        # Add fragment information (2 bytes: fragment_id + total_fragments)
        fragment_info = fragment_id.to_bytes(1, byteorder='big') + total_fragments.to_bytes(1, byteorder='big')

        # Encode data with Hamming74
        encoded_blocks = []
        for i in range(0, len(data), 4):
            block = data[i:i+4]
            encoded, _ = hamming74_encode(block)
            encoded_blocks.append(encoded)
        data_with_hamming = b''.join(encoded_blocks)

        # Define the original length
        original_len = len(data).to_bytes(2, byteorder='big')

        # Calculate CRC
        crc = calc_crc(seq_byte + fragment_info + data_with_hamming + original_len, 0x8005)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        
        # Return combined frame as bytes
        return seq_byte + fragment_info + data_with_hamming + original_len + crc_bytes
    
    @staticmethod
    def create_fragmented_frames(seq_num, data):
        if len(data) <= Frame.FRAGMENT_SIZE:
            # Data is less than or equal to the fragment size, no need to fragment
            return [Frame.create_frame(seq_num, data)]
        
        frames = []
        total_fragments = (len(data) + Frame.FRAGMENT_SIZE - 1) // Frame.FRAGMENT_SIZE
        
        for i in range(total_fragments):
            start = i * Frame.FRAGMENT_SIZE
            end = min(start + Frame.FRAGMENT_SIZE, len(data))
            fragment_data = data[start:end]
            
            frame = Frame.create_frame(seq_num, fragment_data, i, total_fragments)
            frames.append(frame)
        
        return frames
    
    @staticmethod
    def is_fragmented(total_fragments):
        """Check if the frame is fragmented"""
        return total_fragments > 1
    
    @staticmethod
    def check_frame(frame):
        try:
            # Extract seq_num, data and crc
            seq_num = frame[0]
            fragment_id = frame[1]
            total_fragments = frame[2]
            data_with_hamming = frame[3:-4]  # Skip seq_num, fragment_id, total_fragments
            original_len = int.from_bytes(frame[-4:-2], byteorder='big')
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
            fragment_info = fragment_id.to_bytes(1, byteorder='big') + total_fragments.to_bytes(1, byteorder='big')
            original_len_byte = original_len.to_bytes(2, byteorder='big')
            frame_for_crc = seq_byte + fragment_info + data_with_hamming + original_len_byte

            # Calculate CRC
            calculated_crc = calc_crc(frame_for_crc, 0x8005)

            # Compare calculated CRC with received CRC
            if calculated_crc == received_crc:
                return seq_num, decode_data, fragment_id, total_fragments
            else:
                return None, b'CRC error', 0, 0
                
        except Exception as e:
            return None, f'Frame check error: {str(e)}'.encode(), 0, 0
    
# Test
if __name__ == "__main__":
    # Test small data
    data = b'Hello world!'
    frame = Frame.create_frame(1, data)
    result = Frame.check_frame(frame)
    print(f"Small data test: {result}")

    # Test large data fragmentation
    large_data = b'This is a very long message ' * 10
    frames = Frame.create_fragmented_frames(2, large_data)
    for i, frame in enumerate(frames):
        result = Frame.check_frame(frame)
        print(f"Fragment {i+1}: {result}")

