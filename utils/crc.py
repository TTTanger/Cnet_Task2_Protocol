def calc_crc(data: bytes, polynomial: int) -> int:
    """
    Calculate CRC for bytes input
    Input:
        data: bytes (e.g. b'hello')
        polynomial: int (e.g. 0x8005 for CRC-16)
    Output: 
        int: 16-bit CRC value
    """
    crc = 0xFFFF
    
    # Process each byte
    for byte in data:
        # Process each bit in the byte from MSB to LSB
        for i in range(7, -1, -1):
            bit = (byte >> i) & 1
            crc ^= bit << 15  # Add bit at MSB
            if crc & 0x8000:  # If MSB is 1
                crc = (crc << 1) ^ polynomial
            else:
                crc = (crc << 1)
            crc &= 0xFFFF     # Keep 16 bits
    
    return crc

def verify_crc(data: bytes, crc: int) -> bool:
    """
    Verify frame integrity using CRC
    Input:
        data: bytes - data to verify
        crc: int - CRC value to check against
    Output:
        bool: True if CRC matches, False otherwise
    """
    calculated_crc = calc_crc(data, 0x8005)
    return calculated_crc == crc

# Test
if __name__ == "__main__":
    test_data = b"1011"
    print(f"Input bytes: {test_data}")
    crc = calc_crc(test_data, 0x8005)
    print(f"CRC: 0x{crc:04x}")
    print(f"Verification: {verify_crc(test_data, crc)}")