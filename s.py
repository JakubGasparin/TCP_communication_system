import os
import socket
from copy import copy
import random

import libscrc


####### FLAGS ######

ACK = 0
RDY = 1
END = 2
WRT = 3
MPK = 4
PFL = 5
NCK = 6
KAR = 7

####### FLAGS ######


###### GLOBAL VARIABLES ########


HOST = "192.168.56.1"
PORT = 5555
FRAGMENT_SIZE = 200
FRAGMENT_HEAD_SIZE = 13  # STATICKÁ HODNOTA NEMENTO!!!!
OPERATION = 0
SIMULATE_ERROR = False


###### GLOBAL VARIABLES ########


###### FLAG FUNCTION, SAME FOR BOTH PROGRAMS ######


def get_flag(operation):
    if operation == ACK:
        operation = "_ACK"
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
    if operation == PFL:
        operation = "_PFL"
        return operation
    if operation == KAR:
        operation = "_KAR"
        return operation


###### FLAG FUNCTION, SAME FOR BOTH PROGRAMS ######


################################ RECEIVER PROGRAM #############################


def decode_WRT(data, operation, opcode):
    global SIMULATE_ERROR
    order = int.from_bytes(data[:4], "big")
    total_packets = int.from_bytes(data[5:9], "big")
    msg = data[9:-4]
    crc = int.from_bytes(data[-4:], "big")
    checksum = libscrc.buypass(order.to_bytes(4, "big") + operation.to_bytes(1, "big") +
                               total_packets.to_bytes(4, "big") + msg)
    if SIMULATE_ERROR:
        if random.randint(1, 3) == 1:
            checksum = checksum + checksum
            print("Wrong packet, requesting resending...")
    msg = msg.decode()
    if checksum == crc:
        packet = [order, opcode, total_packets,  msg, crc]
        return packet
    else:
        packet = [0, "_NCK", 0, 0, 0]
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
    else:
        packet = [0, "_NCK", 0, 0, 0]
        return packet


def decode_PFL(data, operation, opcode):
    order = int.from_bytes(data[:4], "big")
    total_packets = int.from_bytes(data[5:9], "big")
    msg = data[9:-4]
    crc = int.from_bytes(data[-4:], "big")
    checksum = libscrc.buypass(order.to_bytes(4, "big") + operation.to_bytes(1, "big") +
                               total_packets.to_bytes(4, "big") + msg)
    if SIMULATE_ERROR:
        if random.randint(1, 25) == 1:
            checksum = checksum + checksum
            print("Wrong packet")
    if checksum == crc:
        packet = [order, opcode, total_packets, msg, crc]
        return packet
    else:
        packet = [0, "_NCK", 0, 0, 0]
        return packet


def decode_KAR(data, operation, opcode):
    order = int.from_bytes(data[:4], "big")
    total_packets = int.from_bytes(data[5:9], "big")
    msg = data[9:-4]
    crc = int.from_bytes(data[-4:], "big")
    checksum = libscrc.buypass(order.to_bytes(4, "big") + operation.to_bytes(1, "big") +
                               total_packets.to_bytes(4, "big") + msg)

    if checksum == crc:
        packet = [order, opcode, total_packets, msg, crc]
        return packet


def decode_data(data):
    global OPERATION
    operation = int.from_bytes(data[4:5], "big")
    opcode = get_flag(operation)
    if opcode == "_WRT":
        OPERATION = "_WRT"
        packet = decode_WRT(data, operation, opcode)
        return packet
    if opcode == "_END":
        OPERATION = "_END"
        packet = decode_END(data, operation, opcode)
        return packet
    if opcode == "_PFL":
        OPERATION = "_PFL"
        packet = decode_PFL(data, operation, opcode)
        return packet
    if opcode == "_KAR":
        OPERATION = "_KAR"
        packet = decode_KAR(data, operation, opcode)
        return packet


def encode_ACK():
    order = 0
    opcode = 0
    msg = "Acknowledgement"
    total_packets = 1
    order = order.to_bytes(4, "big")
    opcode = opcode.to_bytes(1, "big")
    total_packets = total_packets.to_bytes(4, "big")
    msg = msg.encode()
    crc = libscrc.buypass(order + opcode + total_packets + msg)
    crc = crc.to_bytes(4, "big")
    packet = order + opcode + total_packets + msg + crc
    return packet

def encode_NCK():
    order = 0
    opcode = 6
    msg = "Not acknowledged"
    total_packets = 1
    order = order.to_bytes(4, "big")
    opcode = opcode.to_bytes(1, "big")
    total_packets = total_packets.to_bytes(4, "big")
    msg = msg.encode()
    crc = libscrc.buypass(order + opcode + total_packets + msg)
    crc = crc.to_bytes(4, "big")
    packet = order + opcode + total_packets + msg + crc
    return packet


def list_to_string(list):
    str = ""
    for i in list:
        str += i
    return str


def bytes_array_to_file(data):
    bytes_array = bytearray()
    for i in data:
        bytes_array += i
    filePath = input("Enter download path: ")
    fileName = input("Enter name of the file: ")
    if os.path.exists(filePath):
        filePath = filePath + "\\" + fileName
        with open(filePath, "wb+") as bin_file:
            bin_file.write(bytes_array)
    print(f"File successfully downloaded on {filePath}")
    return

################################ RECEIVER PROGRAM #############################




################################ DRIVER FUNCTION ##############################

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

                    if packet[1] != "_NCK" and packet[1] != "_KAR":
                        full_msg.append(copy(packet[3]))
                        ACK_packet = encode_ACK()
                        conn.send(ACK_packet)
                    if packet[1] == "_NCK":
                        NCK_packet = encode_NCK()
                        conn.send(NCK_packet)

                    if packet[0] == packet[2] and OPERATION == "_WRT" and packet[1] != "_NCK":
                        str = list_to_string(full_msg)
                        print(str)
                        print("\n")
                        del str
                        full_msg.clear()
                    if packet[0] == packet[2] and OPERATION == "_PFL" and packet[1] != "_NCK":
                        bytes_array_to_file(full_msg)
                        full_msg.clear()




                    #try:
                        #conn.send(data)
                    #except ConnectionResetError as e:
                     #   break

                    #ACK_packet = encode_ACK()
                    #print(f"ack packet {ACK_packet}")
                    #conn.send(ACK_packet)

################################ DRIVER FUNCTION ##############################


# Main function caller
if __name__ == "__main__":
    main()
