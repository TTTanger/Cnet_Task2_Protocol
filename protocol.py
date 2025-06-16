from utils.hamming import hamming74_encode, hamming74_decode
from utils.crc import calc_crc

# Define the frame
class Frame:
    """Create the frame from string data"""
    @staticmethod
    def create_frame(seq_num, data):
        # Add sequence number (1 byte)
        seq_byte = seq_num.to_bytes(1, byteorder='big')

        # Calculate hamming
        data_with_hamming, original_len = hamming74_encode(data)

        # Define the original length
        original_len = original_len.to_bytes(1, byteorder='big')

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

            # First try to decode and fix errors using Hamming code
            try:
                decode_data = hamming74_decode(data_with_hamming, original_len)
            except Exception as e:
                return b'Hamming decode error'

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