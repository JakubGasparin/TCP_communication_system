import socket
import libscrc

HOST = "192.168.56.1"
PORT = 5555
FRAGMENT_SIZE = 1024
PACKET_ORDER = 1


def create_packet():
    global PACKET_ORDER
    msg = input("Insert your message: ").encode()
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
    checksum = checksum.encode()

    msg = order + operation + msg + checksum
    print(msg)
    return msg


def decode_acknowledgement_packet(data):
    msg = data.decode()
    operation = msg[0:3]
    checksum = msg[3:]
    packet = [operation, checksum]
    return packet


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            packet = create_packet()
            print(packet)
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
