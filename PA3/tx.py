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

    #adriana - set timeoout for the socket + added logs
    sock.settimeout(TIMEOUT)
    tx_seq_log = open("TxSeqNum.log", "w")
    tx_ack_log = open("TxAck.log", "w")

    #next i am doing the read file
    with open(filename, "rb") as f:
        file_data = f.read()

    #window using circular queue
    window = CircularQueue(WINDOW_SIZE)

    next_seqnum = 0
    file_index = 0

    while True:

        #fill window (PIPELINE SENDING)
        while not window.isFull() and file_index < len(file_data):
           
           chunk = file_data[file_index:file_index+PAYLOAD_SIZE]

           pkt = Packet(
               flag=1, # data packet
               seqnum=next_seqnum,
                length=len(chunk),
                payload=chunk.decode("utf-8") #dear agafia, im using this to convert bytes to string, if it doesnt work please lmk
           )

          window.enqueue(pkt)

            #set up the sending packet
              sock.send(pkt.serialize())
        tx_seq_log.write(f"{pkt.seqnum}\n")

        file_index +=len(chunk)
        next_seqnum = (next_seqnum + 1) % SEQNUM_SIZE

        #waiting for ack

        try:
            data


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