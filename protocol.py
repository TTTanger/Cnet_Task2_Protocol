# Define the frame
class Frame:
    def __init__(self, data, seq_num, crc):
        self.data = data
        self.seq_num = seq_num
        self.crc = crc

    def to_bytes(self):
        """Convert frame to bytes for transmission"""
        try:
            data_bytes = self.data.encode()
            seq_num_bytes = self.seq_num.to_bytes(1, 'big')
            crc_bytes = self.crc.to_bytes(2, 'big')
            return data_bytes + seq_num_bytes + crc_bytes
        except Exception as e:
            print(f"Error in to_bytes: {e}")
            return None

    @staticmethod
    def from_bytes(frame_bytes):
        """Create frame from received bytes"""
        try:
            if len(frame_bytes) < 3:  # Check minimum length
                raise ValueError("Frame too short")
            
            data = frame_bytes[:-3].decode()
            seq_num = int.from_bytes(frame_bytes[-3:-2], 'big')
            crc = int.from_bytes(frame_bytes[-2:], 'big')
            return Frame(data, seq_num, crc)
        except Exception as e:
            print(f"Error in from_bytes: {e}")
            return None

    @staticmethod
    def create_frame(data, seq_num):
        # Transform the seq_num to bytes
        seq_num_bytes = seq_num.to_bytes(1, 'big')  

        # Combine the data and seq_num
        message = data.encode() + seq_num_bytes

        # Calculate CRC
        crc = Frame.calc_crc(message, 0x8005)

        # Create and return new frame
        return Frame(data, seq_num, crc)

    @staticmethod
    def calc_crc(data, polynomial):
        # Cnit CRC
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc = (crc << 1)
                crc &= 0xFFFF 
        return crc

    def verify_crc(self):
        """Verify frame integrity using CRC"""
        message = self.data.encode() + self.seq_num.to_bytes(1, 'big')
        calculated_crc = self.calc_crc(message, 0x8005)

        if (calculated_crc == self.crc):
            return True
        else:
            return False
