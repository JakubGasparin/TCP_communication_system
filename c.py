import socket
from copy import copy

import libscrc

HOST = "192.168.56.1"
PORT = 5555
FRAGMENT_SIZE = 20
FRAGMENTED_PACKET_FLAG = False
PACKET_ORDER = 1
PACKET_BUFFER = []
DATA = ""


def split_into_fragments(msg):
    global PACKET_ORDER, PACKET_BUFFER, FRAGMENTED_PACKET_FLAG
    FRAGMENTED_PACKET_FLAG = True
    PACKET_BUFFER.clear()
    packet_cut = FRAGMENT_SIZE - 9
    cut_string = [msg[i:i+packet_cut] for i in range(0, len(msg), packet_cut)]
    print(cut_string)

    for i in range(len(cut_string)):
        cut_msg = cut_string[i].encode()
        print(cut_msg)
        order = PACKET_ORDER
        PACKET_ORDER += 1
        order = order.to_bytes(4, "big")
        operation = "001"
        operation = operation.encode()
        crc = libscrc.buypass(order + operation + cut_msg)
        crc = crc.to_bytes(2, "big")

        fragment_msg = order + operation + cut_msg + crc
        PACKET_BUFFER.append(copy(fragment_msg))
        print(PACKET_BUFFER)
        print(len(PACKET_BUFFER[i]))


def create_get_ready_packet():
    order = 0
    order = order.to_bytes(4, "big")
    operation = 'RDY'
    operation = operation.encode()
    crc = libscrc.buypass(order + operation)
    crc = crc.to_bytes(2, "big")
    packet = order + operation + crc
    return packet


def create_packet():
    global PACKET_ORDER, PACKET_BUFFER
    msg = input("Insert your message: ")

    if len(msg) + 9 > FRAGMENT_SIZE:
        split_into_fragments(msg)
        packet = create_get_ready_packet()
        print(packet)
        return packet
    else:
        msg = msg.encode()
        order = PACKET_ORDER
        PACKET_ORDER += 1
        order = order.to_bytes(4, "big")
        operation = '001'
        operation = operation.encode()
        checksum = libscrc.buypass(order + operation + msg)
        checksum = checksum.to_bytes(2, "big")
        msg = order + operation + msg + checksum
        return msg


def decode_acknowledgement_packet(data):
    msg = data.decode()
    operation = msg[0:3]
    checksum = msg[3:]
    packet = [operation, checksum]
    return packet


def main():
    global FRAGMENTED_PACKET_FLAG
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            packet = create_packet()
            print("length: ")
            print(len(packet))
            if FRAGMENTED_PACKET_FLAG:
                for i in range(len(PACKET_BUFFER)):
                    print(PACKET_BUFFER[i])
                    s.send(PACKET_BUFFER[i])
            else:
                s.send(packet)
            data = s.recv(FRAGMENT_SIZE)
            packet_ack = decode_acknowledgement_packet(data)

            print(f"Acknowledged: {packet_ack[0]}\n"
                  f"Checksum: {packet_ack[1]}")
            #print("Received:", data.decode())


if __name__ == "__main__":
    main()
