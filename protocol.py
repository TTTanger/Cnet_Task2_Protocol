from utils.hamming import hamming74
from utils.crc import calc_crc

# Define the frame
class Frame:
    def __init__(self, data_with_hamming, crc):
        self.data_with_hamming = data_with_hamming
        self.crc = crc

    """Create the frame from string data"""
    @staticmethod
    def create_frame(bytes_data):
        # Convert bytes data to binary data
        binary_data = 0
        for char in bytes_data:
            binary_data = binary_data << 8 | ord(char)

        # Calculate hamming
        data_with_hamming = hamming74(binary_data)

        # Calculate CRC
        crc = calc_crc(data_with_hamming, 0x8005)

        # Create and return new frame
        return Frame(data_with_hamming, crc)

    """Before sending, call this method: from the string data to bytes"""
    def to_bytes(self):
        """Convert frame data to bytes for transmission
        Returns: bytes containing encoded data and CRC
        """
        try:
            # Convert binary data to bytes
            data_bytes = self.data_with_hamming.to_bytes(
                (self.data_with_hamming.bit_length() + 7) // 8, 'big'
            )
            # Convert CRC to 2 bytes
            crc_bytes = self.crc.to_bytes(2, 'big')
            
            return data_bytes + crc_bytes
        
        except Exception as e:
            print(f"Error in to_bytes: {e}")
            return None

    @staticmethod
    def from_bytes(frame_bytes):
        """Reconstruct frame from received bytes
        Args: frame_bytes - received bytes containing data and CRC
        Returns: Frame object or None if error
        """
        try:
            if len(frame_bytes) < 3:
                raise ValueError("Frame too short")
            
            # Split into data and CRC
            data_bytes = frame_bytes[:-2]
            crc_bytes = frame_bytes[-2:]
            
            # Convert back to integers
            data_with_hamming = int.from_bytes(data_bytes, 'big')
            crc = int.from_bytes(crc_bytes, 'big')
            
            return Frame(data_with_hamming, crc)
        
        except Exception as e:
            print(f"Error in from_bytes: {e}")
            return None
        
# Test
if __name__ == "__main__":
    data = 'Hello world!'
    frame = Frame.create_frame(data)
    print(bin(frame.data_with_hamming)[2:])
    print(bin(frame.crc)[2:])