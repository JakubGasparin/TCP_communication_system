import socket

import libscrc

HOST = "192.168.56.1"
PORT = 5555
FRAGMENT_SIZE = 1024


def decode_packet(data):
    msg = data.decode()
    order = msg[0:2]
    operation = msg[2:5]
    checksum = msg[-5:]
    msg = msg[:-5]
    data = [msg[5:]]
    crc = libscrc.buypass(msg[0:2].encode() + msg[2:5].encode() + msg[5:].encode())
    crc = str(crc)
    print(crc, checksum)
    if crc == checksum:
        packet = [order, operation, data, checksum]
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
                    print("Received:", data.decode())
                    decoded_packet = decode_packet(data)
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
