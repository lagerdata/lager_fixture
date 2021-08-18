import sys
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
    def __init__(self, serial_port=None, debug=False, print_uart=False):
        self.debug = debug
        self.print_uart = print_uart
        self.ser_queue = queue.Queue()
        self.uart_queue = [queue.Queue()] * 10
        
        if serial_port is not None:
            self.ser = serial.Serial(serial_port, 9600, timeout=0.1)
        else:
            # Use default serial port if available
            try:
                serial_port = "/dev/ttyACM0"
                self.ser = serial.Serial(serial_port, 9600, timeout=0.1)
            except serial.serialutil.SerialException:
               print("ERROR: Failed to open connection to Lager Test Fixture. " \
                     "Check that fixture is attached and that you're connecting with the correct TTY device path.")
               sys.exit(1)

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

    # def handle_UART_RX(self, frame):
    #     channel = frame[1]
    #     if self.print_uart:
    #         print(f"UART {channel}: {frame[2:].decode('ascii')}")
    #     else:
    #         self.uart_queue.put(frame)

    def handle_uart(self, frame):
        channel = frame[1]
        if self.print_uart:
            line = frame[2:].decode('ascii').replace("\r\n", "")
            print(f"UART {channel}: {line}")
        else:
            self.uart_queue[channel].put(frame[2:])
    
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
        
        self.check_queue()

    def check_queue(self, timeout=0.01):
        
        while True:
            try:
                frame = self.ser_queue.get(block=True, timeout=timeout)
                if self.debug: print(f"\tReceived {frame}")

                if frame[0] == UART_RX:
                    self.handle_uart(frame)
                    continue

                try:
                    func_name = "handle_" + CMD_NAMES[frame[0]]
                    func = getattr(self, func_name)
                    return func(frame)
                except (KeyError, AttributeError):
                    if self.debug: print(f"\tGot frame: {frame}")
                    return frame
            except queue.Empty:
                return

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

    def uart_rx(self, channel, block=False, timeout=0.1):
        try:
            return self.uart_queue[channel].get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def uart_tx(self, channel, data):
        length = len(data)
        self.send_cmd_resp(UART_TX, [channel, length] + [ord(c) for c in data])

    def set_freq(self, channel, freq, dc):
        freq_h = freq >> 8
        freq_l = freq & 0xFF
        val = (dc * 255) // 100
        self.send_cmd_resp(SET_PWM, [channel, freq_h, freq_l, val])

    def get_freq(self, channel):
        resp = self.send_cmd_resp(GET_TACH, [channel])
        freq = resp[1] << 8 | resp[2]
        return freq