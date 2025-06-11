from utils.hamming import hamming74_encode, hamming74_decode
from utils.crc import calc_crc

# Define the frame
class Frame:
    """Create the frame from string data"""
    @staticmethod
    def create_frame(data):
        # Calculate hamming
        data_with_hamming, original_len = hamming74_encode(data)

        # Define the original length
        original_len = original_len.to_bytes(1, byteorder='big')

        # Calculate CRC
        crc = calc_crc(data_with_hamming + original_len, 0x8005)

        # Convert CRC to 2 bytes (16 bits)
        crc_bytes = crc.to_bytes(2, byteorder='big')
        
        # Return combined frame as bytes
        return data_with_hamming + original_len + crc_bytes
    
    @staticmethod
    def check_frame(frame):
        try:
            # Extract data and crc
            data_with_hamming = frame[:-3]
            original_len = int.from_bytes(frame[-3:-2], byteorder='big')
            received_crc = int.from_bytes(frame[-2:], byteorder='big')

            # First try to decode and fix errors using Hamming code
            try:
                decode_data = hamming74_decode(data_with_hamming, original_len)
            except Exception as e:
                return b'Hamming decode error'

            # After correction, calculate and check CRC
            calculated_crc = calc_crc(data_with_hamming + original_len.to_bytes(1, byteorder='big'), 0x8005)

            # Compare calculated CRC with received CRC
            if calculated_crc == received_crc:
                return decode_data
            else:
                return b'CRC error'
                
        except Exception as e:
            return f'Frame check error: {str(e)}'.encode()
    
# Test
if __name__ == "__main__":
    data = b'Hello world!'
    frame = Frame.create_frame(data)
    print(f"Frame: {frame.hex()}")
    print(f"Data part: {frame[:-3].hex()}")
    print(f"Length part: {frame[-3:-2].hex()}")
    print(f"CRC part: {frame[-2:].hex()}")
    print(f"Decoded data: {Frame.check_frame(frame)}")