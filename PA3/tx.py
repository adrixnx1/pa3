import socket
import argparse
from pa3.packet import Packet
from pa3.cQueue import CircularQueue

PAYLOAD_SIZE = 50
SEQNUM_SIZE = 10
WINDOW_SIZE = 5
TIMEOUT = 0.5


def reliablyTransfer(rx_ip, rx_port, filename):
    # Implement the UDP sender to reliably transfer the file
    # Create log files as well to log the events in the sender side
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((rx_ip, rx_port))

    # adriana - set timeout for the socket + added logs
    sock.settimeout(TIMEOUT)
    tx_seq_log = open("TxSeqNum.log", "w")
    tx_ack_log = open("TxAck.log", "w")

    # next i am doing the read file
    with open(filename, "rb") as f:
        file_data = f.read()

    # window using circular queue
    window = CircularQueue(WINDOW_SIZE)

    next_seqnum = 0
    file_index = 0

    while True:

        # fill window (PIPELINE SENDING)
        while not window.isFull() and file_index < len(file_data):

            chunk = file_data[file_index:file_index + PAYLOAD_SIZE]

            pkt = Packet(
                flag=1,  # data packet
                seqnum=next_seqnum,
                length=len(chunk),
                payload=chunk.decode("utf-8")  # convert bytes to string for text file
            )

            window.enqueue(pkt)

            # set up the sending packet
            sock.send(pkt.serialize())
            tx_seq_log.write(f"{pkt.seqnum}\n")

            file_index += len(chunk)
            next_seqnum = (next_seqnum + 1) % SEQNUM_SIZE

        # when done sending all packets and window is empty, send FIN
        if file_index >= len(file_data) and window.isEmpty():
            fin_pck = Packet(flag=2, seqnum=next_seqnum, length=0, payload="")
            sock.send(fin_pck.serialize())
            tx_seq_log.write(f"{fin_pck.seqnum}\n")

            # wait for FIN ACK
            while True:
                try:
                    data = sock.recv(2048)
                    finack_pck = Packet.deserialize(data)

                    if finack_pck.flag == 0:
                        tx_ack_log.write(f"{finack_pck.seqnum}\n")

                        if finack_pck.seqnum == fin_pck.seqnum:
                            break

                except socket.timeout:
                    tx_seq_log.write("Timeout\n")
                    sock.send(fin_pck.serialize())
                    tx_seq_log.write(f"{fin_pck.seqnum}\n")

            break

        # waiting for ACK
        try:
            data = sock.recv(2048)
            ack_pck = Packet.deserialize(data)

            # only care about ACK packets
            if ack_pck.flag == 0:
                tx_ack_log.write(f"{ack_pck.seqnum}\n")

                # cumulative ACK -> remove packets up to that seqnum
                while not window.isEmpty():
                    front_pck = window.getFront()
                    window.dequeue()

                    if front_pck.seqnum == ack_pck.seqnum:
                        break

        except socket.timeout:
            # timeout, resend all packets in the window
            tx_seq_log.write("Timeout\n")

            for i in range(window.size):
                idx = (window.front + i) % window.capacity
                pkt = window.arr[idx]

                sock.send(pkt.serialize())
                tx_seq_log.write(f"{pkt.seqnum}\n")

    print("Closing connection")
    sock.close()
    tx_seq_log.close()
    tx_ack_log.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Transmitter")
    parser.add_argument("-ip", metavar="IP address", default="127.0.0.1", type=str, help="Receiver IP address")
    parser.add_argument("-p", metavar="Port number", default=12345, type=int, help="Receiver port number")
    parser.add_argument("-f", metavar="File path", default="data/small.txt", type=str, help="Path to the file to send")

    args = parser.parse_args()

    reliablyTransfer(args.ip, args.p, args.f)