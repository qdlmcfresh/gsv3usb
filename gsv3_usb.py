import serial
import struct
import platform


class MeasurementConverter:
    def convertValue(self, bytes):
        pass


class ForceMeasurementConverterKG(MeasurementConverter):
    def __init__(self, F_n, S_n, u_e):
        self.F_n = F_n
        self.S_n = S_n
        self.u_e = u_e

    def convertValue(self, bytes):
        A = struct.unpack('>H', bytes[1:])[0]
        return (A - 0x8000) * (self.F_n / self.S_n) * (self.u_e / 0x8000)


class GSV3USB:
    def __init__(self, com_port, baudrate=38400):
        com_path = f'/dev/ttyUSB{com_port}' if platform.system(
        ) == 'Linux' else f'COM{com_port}'
        print(f'Using COM: {com_path}')
        self.sensor = serial.Serial(com_path, baudrate)
        self.converter = ForceMeasurementConverterKG(500, 2, 1.05)

    def set_mode(self, text=False, max=False, log=False, window=False):
        x = 0
        if(text):
            x = x | 0b00010
        if(max):
            x = x | 0b00100
        if(log):
            x = x | 0b01000
        if(window):
            x = x | 0b10000
        self.sensor.write(struct.pack('bb', 0x26, x))

    def read_value(self):
        read_val = self.sensor.read(3)
        return self.converter.convertValue(read_val)

    def clear_maximum(self):
        self.sensor.write(b'\x3C')

    def clear_buffer(self):
        self.sensor.write(b'\x25')


def main():
    dev = GSV3USB(11)
    try:
        while True:
            print(dev.read_value())
    except KeyboardInterrupt:
        print("Exiting")
        return


main()
