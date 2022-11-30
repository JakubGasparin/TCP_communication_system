
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
FRAGMENT_HEAD_SIZE = 13  # STATICKÁ HODNOTA NEMENTO!!!!


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


def decode_WRT(data, operation, opcode):
    order = int.from_bytes(data[:4], "big")
    total_packets = int.from_bytes(data[5:9], "big")
    msg = data[9:-4]
    crc = int.from_bytes(data[-4:], "big")
    checksum = libscrc.buypass(order.to_bytes(4, "big") + operation.to_bytes(1, "big") + total_packets.to_bytes(4, "big") + msg)
    msg = msg.decode()
    if checksum == crc:
        packet = [order, opcode, total_packets,  msg, crc]
        return packet


def decode_END(data, operation, opcode):
    order = int.from_bytes(data[:4], "big")
    total_packets = int.from_bytes(data[5:9], "big")
    msg = data[9:-4]
    crc = int.from_bytes(data[-4:], "big")
    checksum = libscrc.buypass(order.to_bytes(4, "big") + operation.to_bytes(1, "big") +
                               total_packets.to_bytes(4, "big") + msg)
    msg = msg.decode()
    if checksum == crc:
        packet = [order, opcode, total_packets, msg, crc]
        return packet


def decode_data(data):
    operation = int.from_bytes(data[4:5], "big")
    opcode = get_flag(operation)
    if opcode == "_WRT":
        packet = decode_WRT(data, operation, opcode)
        return packet
    if opcode == "_END":
        packet = decode_END(data, operation, opcode)
        return packet


def encode_ACK():
    order = 0
    opcode = 0
    msg = "-1"
    crc = libscrc.buypass(order.to_bytes(4, "big") + opcode.to_bytes(1, "big") + msg.encode())
    order = order.to_bytes(4, "big")
    opcode = opcode.to_bytes(1, "big")
    msg = msg.encode()
    crc = crc.to_bytes(4, "big")
    packet = order + opcode + msg + crc
    return packet


def list_to_string(list):
    str = ""
    for i in list:
        str += i
    return str


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                full_msg = []
                print("Connected to", addr)
                while True:
                    data = conn.recv(FRAGMENT_SIZE)
                    print(data)
                    if not data:
                        break
                    packet = decode_data(data)
                    print(f"Order: {packet[0]}\n"
                          f"Operation: {packet[1]}\n"
                          f"Total_packets: {packet[2]}\n"
                          f"Message: {packet[3]}\n"
                          f"Checksum: {packet[4]}\n")
                    full_msg.append(copy(packet[3]))
                    if packet[0] == packet[2]:
                        str = list_to_string(full_msg)
                        print(str)
                        print("\n")
                        str = ""


                    #try:
                        #conn.send(data)
                    #except ConnectionResetError as e:
                     #   break

                    #ACK_packet = encode_ACK()
                    #print(f"ack packet {ACK_packet}")
                    #conn.send(ACK_packet)


if __name__ == "__main__":
    main()
