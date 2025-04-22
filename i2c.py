
import fcntl
import os

# Constants from <linux/i2c-dev.h>
I2C_SLAVE = 0x0703

class I2CDevice:
    def __init__(self, bus_num, address):
        self.bus_path = f"/dev/i2c-{bus_num}"
        self.address = address
        self.file = os.open(self.bus_path, os.O_RDWR)
        fcntl.ioctl(self.file, I2C_SLAVE, address)

    def write_byte_data(self, reg, value):
        os.write(self.file, bytes([reg, value]))

    def read_byte_data(self, reg):
        os.write(self.file, bytes([reg]))
        return os.read(self.file, 1)[0]

    def read_word_data(self, reg):
        os.write(self.file, bytes([reg]))
        data = os.read(self.file, 2)
        return data[1] << 8 | data[0]  # little-endian

    def close(self):
        os.close(self.file)
