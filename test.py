# unicode string
import socket
import copy
import multiprocessing
import time
import sys
import os
import select
import zlib
import libscrc
string = "lorem ipsum lorem ipsum 11111 2222233333123456"
order = '12'
operation = '001'
testing = 10
# print string
print('The string is:', string)

# default encoding to utf-8
string_utf = string.encode()
order_utf = order.encode()
operation_utf = operation.encode()

msg = order_utf + operation_utf + string_utf
checksum = libscrc.buypass(order_utf + operation_utf + string_utf)
checksum = str(checksum)
checksum = checksum.encode()
# checksum = checksum.to_bytes(2, "big")

msg = msg + checksum

# print result
print('The encoded version is:', string_utf)
print('The encoded version is:', operation_utf)
print('The encoded version is:', order_utf)
print(msg)

print(len(string_utf))

msg = msg.decode()
print(msg)
print(type(msg))
print(msg[0:2])
print(msg[2:5])
print(msg[-5:])
msg = msg[:-5]
data = msg[5:]
print(msg, data)

crc = libscrc.buypass(msg[0:2].encode() + msg[2:5].encode() + msg[5:].encode())
print(crc)

n = 10
print([string[i:i+n] for i in range(0, len(string), n)])

cut_string = [string[i:i+n] for i in range(0, len(string), n)]
print(cut_string)
operation = ''
operation = 'RDY'
print(operation)



