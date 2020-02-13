import serial

class SerialComm:
    def __init__(self, port_in, port_out):
        self.serial_in = serial.Serial(port_in, timeout=1)
        self.serial_out = serial.Serial(port_out)

        self.signal_strength = 0
    def initialize(self):

    def read(self):

    def test_signal(self):

    def write(self, message):
        ser.write(message)
        ser.flush()



serial_out.write("AT")