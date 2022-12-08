import os
import socket
import sys
import threading
import time
from copy import copy
import random
import libscrc

####### FLAGS ######

ACK = 0  # Acknowledgement
RDY = 1  # Ready for communication
END = 2  # End of communication
WRT = 3  # Write a message (from command prompt)
MPK = 4  # Multiple packets
PFL = 5  # File packet  (i.e. sending .jpg, or .docx)
NCK = 6  # Not Acknowledged
KAR = 7  # Keep Alive Request
SWR = 8  # Switch Roles
FIN = 9  # Finish communication

####### FLAGS ######


#HOST = "192.168.56.1"
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5555
FRAGMENT_SIZE = 200
PACKET_ORDER = 1
OPERATION = 0
FRAGMENT_HEAD_SIZE = 13  # STATICKÁ HODNOTA NEMENTO!!!!
GLOBAL_MESSAGE = ""
GLOBAL_MESSAGE_COUNTER = 0
PACKET_BUFFER = []
MULTIPLE_FRAGMENTS_FLAG = False
SIMULATE_ERROR = True

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
    if operation == NCK:
        operation = "_NCK"
        return operation
    if operation == SWR:
        operation = "_SWR"
        return operation
    if operation == FIN:
        operation = "_FIN"
        return operation

###### FLAG FUNCTION, SAME FOR BOTH PROGRAMS ######


################## SENDER CODE #################################################


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
        operation = OPERATION
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

def encode_file_packets(fileContent):
    global PACKET_ORDER, PACKET_BUFFER
    PACKET_BUFFER.clear()
    packet_cut = FRAGMENT_SIZE - FRAGMENT_HEAD_SIZE
    cut_string = [fileContent[i:i + packet_cut] for i in range(0, len(fileContent), packet_cut)]

    for i in range(len(cut_string)):
        order = PACKET_ORDER
        PACKET_ORDER += 1
        order = order.to_bytes(4, "big")
        operation = OPERATION
        operation = operation.to_bytes(1, "big")
        total_packets = len(cut_string)
        total_packets = total_packets.to_bytes(4, "big")
        cut_data = cut_string[i]
        crc = libscrc.buypass(order + operation + total_packets + cut_data)
        crc = crc.to_bytes(4, "big")
        fragment_msg = order + operation + total_packets + cut_data + crc
        PACKET_BUFFER.append(copy(fragment_msg))

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
    total_packets = int.from_bytes(data[5:9], "big")
    msg = data[9:-4]
    msg = msg.decode()
    crc = int.from_bytes(data[-4:], "big")
    checksum = libscrc.buypass(order.to_bytes(4, "big") + operation.to_bytes(1, "big") +
                               total_packets.to_bytes(4, "big") + msg.encode())
    opcode = get_flag(operation)
    if checksum == crc:
        packet = [order, opcode, total_packets, msg,  crc]
        return packet


def encode_KAR():
    order = 0
    operation = KAR
    total_packets = 1
    msg = "Keep alive request"
    order = order.to_bytes(4, "big")
    operation = operation.to_bytes(1, "big")
    total_packets = total_packets.to_bytes(4, "big")
    msg = msg.encode()
    crc = libscrc.buypass(order + operation + total_packets + msg)
    crc = crc.to_bytes(4, "big")
    packet = order + operation + total_packets + msg + crc
    return packet


def send_keep_alive_request(s):
    while True:
        KAR_packet = encode_KAR()
        time.sleep(60)
        print("Sending Keep alive request")
        s.send(KAR_packet)

def encode_SWR():
    order = 0
    operation = SWR
    total_packets = 1
    msg = "Switch Roles"
    order = order.to_bytes(4, "big")
    operation = operation.to_bytes(1, "big")
    total_packets = total_packets.to_bytes(4, "big")
    msg = msg.encode()
    crc = libscrc.buypass(order + operation + total_packets + msg)
    crc = crc.to_bytes(4, "big")
    packet = order + operation + total_packets + msg + crc
    return packet

def encode_FIN():
    order = 0
    operation = FIN
    total_packets = 1
    msg = "Finish"
    order = order.to_bytes(4, "big")
    operation = operation.to_bytes(1, "big")
    total_packets = total_packets.to_bytes(4, "big")
    msg = msg.encode()
    crc = libscrc.buypass(order + operation + total_packets + msg)
    crc = crc.to_bytes(4, "big")
    packet = order + operation + total_packets + msg + crc
    return packet

################## SENDER CODE #################################################

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


def decode_SWR(data, operation, opcode):
    order = int.from_bytes(data[:4], "big")
    total_packets = int.from_bytes(data[5:9], "big")
    msg = data[9:-4]
    crc = int.from_bytes(data[-4:], "big")
    checksum = libscrc.buypass(order.to_bytes(4, "big") + operation.to_bytes(1, "big") +
                               total_packets.to_bytes(4, "big") + msg)

    if checksum == crc:
        packet = [order, opcode, total_packets, msg, crc]
        return packet

def decode_FIN(data, operation, opcode):
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
    if opcode == "_SWR":
        OPERATION = "_SWR"
        packet = decode_SWR(data, operation, opcode)
        return packet
    if opcode == "_FIN":
        OPERATION = "_FIN"
        packet = decode_FIN(data, operation, opcode)
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


################################ SERVER CODE FUNCTION ##############################

def server():
    global FRAGMENT_SIZE, HOST, PORT
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        HOST = input(f"Current host name is {HOST}, select your new host"
                     f" (or type the same address to keep the current host): \n")
        PORT = int(input(f"Default port of this program is {PORT}, "
                         f"select your new port or keep the same port by typing in the current port value: \n"))
        FRAGMENT_SIZE = int(input("Choose fragment size: \n"))
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
                    print(f"Length of fragment: {len(data)}\n"
                          f"Order: {packet[0]}\n"
                          f"Operation: {packet[1]}\n"
                          f"Total_packets: {packet[2]}\n"
                          f"Message: {packet[3]}\n"
                          f"Checksum: {packet[4]}\n")

                    if packet[1] == "_SWR":
                        conn.close()
                        client()
                    if packet[1] == "_FIN":
                        print(f"Connection with {addr} ended.\n")
                        ACK_packet = encode_ACK()
                        conn.send(ACK_packet)
                        conn.close()
                        return


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

################################ SERVER CODE FUNCTION ##############################


################################ CLIENT FUNCTION CODE ##############################


def client():
    i = 0
    global MULTIPLE_FRAGMENTS_FLAG, PACKET_ORDER, OPERATION, FRAGMENT_SIZE, HOST, PORT
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        HOST = input(f"Current host name is {HOST}, select your new host"
                     f" (or type the same address to keep the current host): \n ")
        PORT = int(input(f"Default port of this program is {PORT}, "
                         f"select your new port or keep the same port by typing in the current port value: \n"))
        FRAGMENT_SIZE = int(input("Choose fragment size: \n"))
        s.connect((HOST, PORT))

        ### THREAD ###
        keep_alive_thread = threading.Thread(target=send_keep_alive_request, args=(s,))
        keep_alive_thread.start()
        ### THREAD ###

        while True:
            packetType = input("Are you sending a message or a file, switching roles or ending communication"
                               "?\n (msg/file/switch/end)\n")


            ### MESSAGE ################################################

            if packetType == "msg":
                OPERATION = WRT
                msg = input("Enter message: ")
                encode_multiple_packets(msg)
                for i in range(len(PACKET_BUFFER)):
                    s.send(PACKET_BUFFER[i])

                    ACK_packet = s.recv(FRAGMENT_SIZE)
                    ACK_packet = decode_ACK(ACK_packet)

                    while ACK_packet[1] == "_NCK":
                        print(f"Failed to send packet number {i}, resending packet...\n")
                        s.send(PACKET_BUFFER[i])
                        ACK_packet = s.recv(FRAGMENT_SIZE)
                        ACK_packet = decode_ACK(ACK_packet)

                    print(f"Packet number {i} was sent successfully. Yay :D\n")

            ### MESSAGE ################################################


            ### FILE ################################################

            elif packetType == "file":
                OPERATION = PFL
                filePath = input("Enter filepath to your file you wish to send: ")
                fileName = input("Enter filename of the file you wish to send: ")
                if os.path.exists(filePath):
                    filePath = filePath + "\\" + fileName
                    if os.path.exists(filePath):
                        with open(filePath, "rb") as bin_file:
                            fileContent = bin_file.read()
                        encode_file_packets(fileContent)
                        for i in range(len(PACKET_BUFFER)):
                            print(PACKET_BUFFER[i])
                            s.send(PACKET_BUFFER[i])

                            ACK_packet = s.recv(FRAGMENT_SIZE)
                            ACK_packet = decode_ACK(ACK_packet)

                            while ACK_packet[1] == "_NCK":
                                print(f"Failed to send packet number {i}, resending packet...\n")
                                s.send(PACKET_BUFFER[i])
                                ACK_packet = s.recv(FRAGMENT_SIZE)
                                ACK_packet = decode_ACK(ACK_packet)

                            print(f"Packet number {i} was sent successfully. Yay :D\n")


                    else:
                        print("File does not exist")
                else:
                    print("Directory or patch to it does not exist")

                ### FILE ################################################
            elif packetType == "switch":
                SWR_packet = encode_SWR()
                s.send(SWR_packet)
                s.close()
                server()

            elif packetType == "end":
                FIN_packet = encode_FIN()
                s.send(FIN_packet)
                ACK_packet = s.recv(FRAGMENT_SIZE)
                print(ACK_packet)
                return

            else:
                print("\n")

            OPERATION = 0
            PACKET_ORDER = 1

################################ CLIENT FUNCTION CODE ##############################


# Main function caller. This code will always start as client.
if __name__ == "__main__":
    client()
