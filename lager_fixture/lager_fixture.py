import queue
import serial
from .simple_hdlc import HDLC

ACK = 0x01
NACK = 0x02
PING = 0x0A
GPIO_GET = 0x0B
MODE = 0x0C
COMM = 0x0D
GPIO_SET = 0x0E
UART_RX = 0x5A
UART_TX = 0x6A
I2C_TX = 0x7A
I2C_RX = 0x7B
SPI_XFER = 0x8A
SET_PWM = 0x9A
GET_TACH = 0xAA

CMD_NAMES = {0x01: "ACK", 0x02: "NACK", 0x0A: "PING", 0x0B: "GPIO_GET", \
             0x0C: "MODE", 0x0D: "COMM", 0x0E: "GPIO_SET", \
             0x5A: "UART_RX", 0x6A: "UART_TX", \
             0x7A: "I2C_TX", 0x7B: "I2C_RX", 0x8A: "SPI_XFER", 0x9A: "SET_PWM", 0xAA: "GET_TACH" }

INPUT = 0
OUTPUT = 1

HIGH = 1
LOW = 0

class LagerFixture:
    def __init__(self, serial_port, debug=False):
        self.debug = debug
        self.ser_queue = queue.Queue()
        
        self.ser = serial.Serial(serial_port, 9600, timeout=0.1)
        self.reset()

    def reset(self):
        self.ser.flushInput()
        self.h = HDLC(self.ser, self.debug)
        self.h.startReader(self.got_frame)

    def handle_ACK(self, frame):
        if self.debug: print("\tCommand Acknowledged!")

    def handle_NACK(self, frame):
        if self.debug: print("\tCommand Error!")

    def handle_GPIO_GET(self, frame):
        return [b > 0 for b in frame[1:]]

    def send_cmd(self, cmd, data=None):
        output = bytearray()
        output.append(cmd)
        if data:
            output.extend(data)
        self.h.sendFrame(output)

    def send_cmd_resp(self, cmd, data=None, timeout=0.5):
        if self.debug: 
            if data != None:
                print(f"Sending {CMD_NAMES[cmd]}: {' '.join([hex(d) for d in data])}")
            else:
                print(f"Sending {CMD_NAMES[cmd]} (No Data)")
        self.send_cmd(cmd, data)
        
        frame = self.ser_queue.get(block=True, timeout=timeout)
        if self.debug: print(f"\tReceived {frame}")
        try:
            func_name = "handle_" + CMD_NAMES[frame[0]]
            func = getattr(self, func_name)
            return func(frame)
        except (KeyError, AttributeError):
            if self.debug: print(f"\tGot frame: {frame}")
            return frame

    def got_frame(self, frame):
        self.ser_queue.put(frame)

    def set_gpio_mode(self, pin, direction):
        self.send_cmd_resp(MODE, [pin, direction])

    def set_gpio(self, pin, level):
        self.send_cmd_resp(GPIO_SET, [pin, level])

    def get_gpio(self, pin):
        resp = self.send_cmd_resp(GPIO_GET)
        return resp[pin]

    def i2c_tx(self, channel, target, data):
        length = len(data)
        self.send_cmd_resp(I2C_TX, [channel, target, length] + data)

    def i2c_rx(self, channel, target, length):
        resp = self.send_cmd_resp(I2C_RX, [channel, target, length])
        return resp

    def spi_xfer(self, channel, ss, data):
        length = len(data)
        resp = self.send_cmd_resp(SPI_XFER, [channel, ss, length] + data)
        return resp

    def uart_rx(self, channel):
        resp = self.send_cmd_resp(UART_RX, [channel])
        if resp is not None:
            return resp.decode("ascii")

    def uart_tx(self, channel, data):
        length = len(data)
        self.send_cmd_resp(UART_TX, [channel, length] + [ord(c) for c in data])

    def set_pwm(self, channel, freq, val):
        freq_h = freq >> 8
        freq_l = freq & 0xFF
        self.send_cmd_resp(SET_PWM, [channel, freq_h, freq_l, val])

    def get_tach(self, channel):
        resp = self.send_cmd_resp(GET_TACH, [channel])
        freq = resp[1] << 8 | resp[2]
        return freq