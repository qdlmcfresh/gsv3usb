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

    def convertValue(self, value):
        A = struct.unpack('>H', value)[0]
        # return (A - 0x8000) * (self.F_n / self.S_n) * (self.u_e / 0x8000)
        return self.F_n / self.S_n * ((A - 0x8000) / 0x8000) * self.u_e * 2


class GSV3USB:
    def __init__(self, com_port, baudrate=38400):
        com_path = f'/dev/ttyUSB{com_port}' if platform.system(
        ) == 'Linux' else f'COM{com_port}'
        print(f'Using COM: {com_path}')
        self.sensor = serial.Serial(com_path, baudrate)
        self.converter = ForceMeasurementConverterKG(500, 2, 1.05)

    def get_all(self, profile=0):
        self.sensor.write(struct.pack('bb', 9, profile))

    def save_all(self, profile=2):
        self.sensor.write(struct.pack('bb', 10, profile))

    def start_transmission(self):
        self.sensor.write(b'\x23')

    def stop_transmission(self):
        self.sensor.write(b'\x24')

    def set_zero(self):
        self.sensor.write(b'\x0C')

    def set_offset(self):
        self.sensor.write(b'\x0E')

    def set_bipolar(self):
        self.sensor.write(b'\x14')

    def set_unipolar(self):
        self.sensor.write(b'\x15')

    def get_serial_nr(self):
        self.stop_transmission()
        self.sensor.write(b'\x1F')
        ret = self.sensor.read(8)
        self.start_transmission()
        return ret

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

    def get_mode(self):
        self.stop_transmission()
        self.sensor.write(b'\x27')
        ret = self.sensor.read(1)
        self.start_transmission()
        return ret

    def get_firmware_version(self):
        self.stop_transmission()
        self.sensor.write(b'\x27')
        ret = self.sensor.read(2)
        self.start_transmission()
        return ret

    def get_special_mode(self):
        self.stop_transmission()
        self.sensor.write(b'\x89')
        ret = self.sensor.read(2)
        self.start_transmission()
        return ret

    def set_special_mode(self):
        pass

    def read_value(self):
        self.sensor.read_until(b'\xA5')
        read_val = self.sensor.read(2)
        return self.converter.convertValue(read_val)

    def clear_maximum(self):
        self.sensor.write(b'\x3C')

    def clear_buffer(self):
        self.sensor.write(b'\x25')


def main():
    dev = GSV3USB(10)
    try:
        while True:
            print(dev.read_value())
    except KeyboardInterrupt:
        print("Exiting")
        return


if __name__ == "__main__":
    main()
