import socket
import argparse
from pa3.packet import Packet
from pa3.cQueue import CircularQueue


PAYLOAD_SIZE = 50
SEQNUM_SIZE = 10
WINDOW_SIZE = 5


def reliablyTransfer(rx_ip, rx_port, filename):
    # Implement the UDP sender to reliably transfer the file
    # Create log files as well to log the events in the sender side
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((rx_ip, rx_port))
    sock.send(b"hi!")
    # TODO: later, loop until FINACK is received (I think)
    msg_recv = sock.recv(50)
    print(f"Received the message: {msg_recv}")

    # TODO: log messages to log file, not console
    print("Closing connection")
    sock.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Transmitter")
    parser.add_argument("-ip", metavar="IP address", default="127.0.0.1", type=str, help="Receiver IP address")
    parser.add_argument("-p", metavar="Port number", default=12345, type=int, help="Receiver port number")
    parser.add_argument("-f", metavar="File path", default="data/small.txt", type=str, help="Path to the file to send")

    args = parser.parse_args()

    reliablyTransfer(args.ip, args.p, args.f)