def calc_crc(binary_data, polynomial):
    """
    Calculate CRC for binary integer input
    Input: binary integer (e.g. 0b1011)
    Output: 16-bit CRC value
    """
    crc = 0xFFFF
    data = binary_data
    
    # Get number of bits in input
    if data == 0:
        num_bits = 1
    else:
        num_bits = data.bit_length()
    
    # Process each bit from MSB to LSB
    for i in range(num_bits-1, -1, -1):
        bit = (data >> i) & 1
        crc ^= bit << 15  # Add bit at MSB
        if crc & 0x8000:  # If MSB is 1
            crc = (crc << 1) ^ polynomial
        else:
            crc = (crc << 1)
        crc &= 0xFFFF     # Keep 16 bits
    
    return crc

def verify_crc(binary_data, crc):
    """Verify frame integrity using CRC"""
    calculated_crc = calc_crc(binary_data, 0x8005)
    return calculated_crc == crc

# Test
if __name__ == "__main__":
    test_data = 0b1011
    print(f"Input binary: {bin(test_data)[2:]}")
    crc = calc_crc(test_data, 0x8005)
    print(f"CRC: 0x{crc:04x}")
    print(f"Verification: {verify_crc(test_data, crc)}")