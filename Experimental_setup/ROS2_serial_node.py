import rclpy
from rclpy.node import Node
import serial


class SerialNode(Node):
    def __init__(self):
        super().__init__('serialnode')
        self.timer = self.create_timer(1, self.timer_callback)

        self.ser = serial.Serial("/dev/ttyUSB0", baudrate=9600)
        if self.ser.is_open:
            self.get_logger().info('Serial opened!')

    def timer_callback(self):
        while self.ser.is_open:
            self.ser.write(bytes(b'I am active'))
            self.get_logger().info('Message sent')

def main(args=None):
    rclpy.init(args=args)
    serialnode = SerialNode()
    rclpy.spin(serialnode)

if __name__ == '__main__':
    main()
