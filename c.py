import socket
from copy import copy

import libscrc

####### FLAGS ######

ACK = 0
RDY = 1
END = 2
WRT = 3
MPK = 4

####### FLAGS ######


HOST = "192.168.56.1"
PORT = 5555
FRAGMENT_SIZE = 50
PACKET_ORDER = 1
OPERATION = ""
FRAGMENT_HEAD_SIZE = 13  # STATICKÁ HODNOTA NEMENTO!!!!
GLOBAL_MESSAGE = ""
GLOBAL_MESSAGE_COUNTER = 0
PACKET_BUFFER = []
MULTIPLE_FRAGMENTS_FLAG = False


def get_flag(operation):
    if operation == ACK:
        operation = "_ACL"
        return operation
    if operation == RDY:
        operation = "_RDY"
        return operation
    if operation == END:
        operation = "_END"
        return operation
    if operation == WRT:
        operation = "_WRT"
        return operation


def encode_single_packet(msg):
    global PACKET_ORDER
    order = PACKET_ORDER
    PACKET_ORDER += 1
    order = order.to_bytes(4, "big")
    operation = 3
    operation = operation.to_bytes(1, "big")
    msg = msg.encode()
    crc = libscrc.buypass(order + operation + msg)
    crc = crc.to_bytes(4, "big")
    packet = order + operation + msg + crc
    return packet


def create_END_packet():
    global PACKET_BUFFER, PACKET_ORDER
    order = PACKET_ORDER
    PACKET_ORDER += 1
    operation = 2
    msg = "-1"
    order = order.to_bytes(4, "big")
    operation = operation.to_bytes(1, "big")
    msg = msg.encode()
    crc = libscrc.buypass(order + operation + msg)
    crc = crc.to_bytes(4, "big")
    packet = order + operation + msg + crc
    PACKET_BUFFER.append(copy(packet))


def encode_multiple_packets(msg):
    global PACKET_ORDER, PACKET_BUFFER, GLOBAL_MESSAGE_COUNTER
    PACKET_BUFFER.clear()
    packet_cut = FRAGMENT_SIZE - FRAGMENT_HEAD_SIZE
    cut_string = [msg[i:i + packet_cut] for i in range(0, len(msg), packet_cut)]

    for i in range(len(cut_string)):
        order = PACKET_ORDER
        PACKET_ORDER += 1
        order = order.to_bytes(4, "big")
        operation = 3
        operation = operation.to_bytes(1, "big")
        total_packets = len(cut_string)
        total_packets = total_packets.to_bytes(4, "big")
        cut_msg = cut_string[i].encode()
        crc = libscrc.buypass(order + operation + total_packets + cut_msg)
        crc = crc.to_bytes(4, "big")
        fragment_msg = order + operation + total_packets + cut_msg + crc
        PACKET_BUFFER.append(copy(fragment_msg))

    # create_END_packet()
    print(PACKET_BUFFER)


def encode_data():
    global GLOBAL_MESSAGE, MULTIPLE_FRAGMENTS_FLAG
    msg = input("Please write your message: ")
    if len(msg) + FRAGMENT_HEAD_SIZE > FRAGMENT_SIZE:
        MULTIPLE_FRAGMENTS_FLAG = True
        encode_multiple_packets(msg)
        return 0
    else:
        packet = encode_single_packet(msg)
        return packet


def decode_ACK(data):
    order = int.from_bytes(data[:4], "big")
    operation = int.from_bytes(data[4:5], "big")
    opcode = get_flag(operation)
    msg = data[5:-4]
    msg = msg.decode()
    crc = int.from_bytes(data[-4:], "big")
    checksum = libscrc.buypass(order.to_bytes(4, "big") + operation.to_bytes(1, "big") + msg.encode())
    if checksum == crc:
        packet = [order, opcode, crc]
        return packet


def main():
    i = 0
    global MULTIPLE_FRAGMENTS_FLAG, PACKET_ORDER
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            msg = input("Enter message: ")
            encode_multiple_packets(msg)
            for i in range(len(PACKET_BUFFER)):
                print(PACKET_BUFFER[i])
                s.send(PACKET_BUFFER[i])
            PACKET_ORDER = 1




            #send_packet = encode_data()
            #if MULTIPLE_FRAGMENTS_FLAG:
            #   for i in range(len(PACKET_BUFFER)):
            #       print(PACKET_BUFFER[i])
            #       s.send(PACKET_BUFFER[i])
            #   MULTIPLE_FRAGMENTS_FLAG = False
            #else:
            #   print("got here")
    #   s.send(send_packet)
            #data = s.recv(FRAGMENT_SIZE)
            #print(f"ack packet {data}")
            #if not data:
            #   break
            #packet = decode_ACK(data)
            #print(f"Acknowledgement packet: \n"
                #     f"Order: {packet[0]}\n"
                # f"Operation: {packet[1]}\n"
            # f"Checksum: {packet[2]}\n")


if __name__ == "__main__":
    main()
