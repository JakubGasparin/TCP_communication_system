import socket

import libscrc

HOST = "192.168.56.1"
PORT = 5555
FRAGMENT_SIZE = 20
OPERATION = ""
PACKET_BUFFER = []
ORDER_BUFFER = []


def decode_get_ready_packet(data):
    global OPERATION
    order = int.from_bytes(data[:4], "big")
    checksum = int.from_bytes(data[-2:], "big")
    data = data[4:]  # odstránim order
    data = data[:-2]  # odstránim crc
    operation = data.decode()
    packet = [order, operation, checksum]
    OPERATION = 'RDY'
    return packet


def decode_packet(data):
    print(data)
    order = int.from_bytes(data[:4], "big")
    checksum = int.from_bytes(data[-2:], "big")
    data = data[4:]     # odstránim order
    data = data[:-2]    # odstránim crc
    print(data)
    data = data.decode()
    operation = data[0:3]
    if operation == 'RDY':
        packet = decode_get_ready_packet(data)
        return packet
    msg = data[3:]
    # data = [msg[6:]]
    crc = libscrc.buypass(order.to_bytes(2, 'big') + data[0:3].encode() + data[3:].encode())
    print(crc, checksum)
    if crc == checksum:
        packet = [order, operation, msg, checksum]
        return packet
    else:
        packet = [0, 0, 0, 0]
        return packet


def encode_acknowledgement_packet():
    operation = 'ACK'
    operation = operation.encode()
    checksum = libscrc.buypass(operation)
    checksum = str(checksum)
    checksum = checksum.encode()
    packet = operation + checksum
    return packet


def main():
    global OPERATION
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print("Connected to", addr)
                while True:
                    data = conn.recv(FRAGMENT_SIZE)
                    if not data:
                        break
                    # print("Received:", data.decode())
                    decoded_packet = decode_packet(data)
                    print(f"Received:{decoded_packet}\n")
                    if OPERATION == 'RDY':
                        print(f"Order of packet: {decoded_packet[0]}\n"
                              f"Ready Operation: {decoded_packet[1]}\n"
                              f"Checksum {decoded_packet[2]}")
                        OPERATION = False
                    else:
                        print(f"Order of packet: {decoded_packet[0]}\n"
                              f"Operation: {decoded_packet[1]}\n"
                              f"Data: {decoded_packet[2]}\n"
                              f"Checksum{decoded_packet[3]}\n")
                    sent_packet = encode_acknowledgement_packet()
                   # sent = input("> ").encode()
                    try:
                        conn.send(sent_packet)
                    except ConnectionResetError as e:
                        break


if __name__ == "__main__":
    main()
