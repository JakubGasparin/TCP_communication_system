import socket
from copy import copy

import libscrc

HOST = "192.168.56.1"
PORT = 5555
FRAGMENT_SIZE = 50
FRAGMENTED_PACKET_FLAG = False
PACKET_ORDER = 1
PACKET_BUFFER = []
DATA = ""


def split_into_fragments(msg):
    global PACKET_ORDER, PACKET_BUFFER, FRAGMENTED_PACKET_FLAG
    FRAGMENTED_PACKET_FLAG = True
    PACKET_BUFFER.clear()
    packet_cut = FRAGMENT_SIZE - 10
    cut_string = [msg[i:i+packet_cut] for i in range(0, len(msg), packet_cut)]
    print(cut_string)

    for i in range (len(cut_string)):
        cut_msg = cut_string[i].encode()
        print(cut_msg)
        order = PACKET_ORDER
        PACKET_ORDER += 1
        if order < 10:
            order = str(order)
            order = '0' + order
            order = order.encode()
        else:
            order = str(order)
            order = order.encode()
        print(order)
        operation = "001"
        operation = operation.encode()
        crc = libscrc.buypass(order + operation + cut_msg)
        crc = str(crc)
        if len(crc) < 5:
            crc = crc + '0'
        crc = crc.encode()

        fragment_msg = order + operation + cut_msg + crc
        PACKET_BUFFER.append(copy(fragment_msg))
        print(PACKET_BUFFER)
        print(len(PACKET_BUFFER[i]))


def create_get_ready_packet():
    order = '00'
    order = order.encode()
    operation = 'RDY'
    operation = operation.encode()
    crc = libscrc.buypass(order + operation)
    crc = str(crc)
    if len(crc) < 5:
        crc = crc + '0'
        crc = crc.encode()
    else:
        crc = crc.encode()
    packet = order + operation + crc
    return packet


def create_packet():
    global PACKET_ORDER, PACKET_BUFFER
    msg = input("Insert your message: ")

    if len(msg) + 10 > FRAGMENT_SIZE:
        split_into_fragments(msg)
        packet = create_get_ready_packet()
        print(packet)
        return packet
    else:
        msg = msg.encode()
        order = PACKET_ORDER
        PACKET_ORDER += 1
        if order < 10:
            order = str(order)
            order = '0' + order
        else:
            order = str(order)
        operation = '001'
        order = order.encode()
        operation = operation.encode()

        checksum = libscrc.buypass(order + operation + msg)
        checksum = str(checksum)
        if len(checksum) < 5:
            checksum = checksum + '0' # uistím sa že checksum vždy bude 5 cifier
        checksum = checksum.encode()
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
            s.send(packet)
            print(len(packet))
            if FRAGMENTED_PACKET_FLAG:
                for i in range (len(PACKET_BUFFER)):
                    print(PACKET_BUFFER[i])
                    s.send(PACKET_BUFFER[i])
            else:
                s.send(packet)
            #sent = input("> ").encode()
            #s.send(sent)
            data = s.recv(FRAGMENT_SIZE)
            packet_ack = decode_acknowledgement_packet(data)

            print(f"Acknowledged: {packet_ack[0]}\n"
                  f"Checksum: {packet_ack[1]}")
            #print("Received:", data.decode())


if __name__ == "__main__":
    main()
