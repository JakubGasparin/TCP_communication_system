# unicode string
import socket
import copy
import multiprocessing
import struct
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


crc = 825

crc = str(crc)

while len(crc) != 5:
    crc = crc + '0'

print(crc)
string = "MKNDKJASNDCôASJKCNASôODMNASôLDNASôLKMDKLôSS!!!éíáýžťčšľ+12324789?:"
string_utf = string.encode()
order = 3
order = order.to_bytes(4, 'big')
crc = libscrc.buypass(order + string_utf + operation_utf)
print(crc)

crc = crc.to_bytes(2, "big")
operation = "WRT"
operation = operation.encode()

msg = order + operation + string_utf + crc
print(msg)

msg_order = int.from_bytes(msg[:4], "big")
msg_crc = int.from_bytes(msg[-2:], "big")
op_utf = msg[4:7]
msg_utf = msg[7:-2]
msg_utf = msg_utf.decode()
op_utf = op_utf.decode()

# filePath = input("Enter file path: ")
# print(filePath)


#  with open("files/files.txt", "rb") as bin_file:
#  fileContent = bin_file.read()


#  if os.path.exists(filePath):
#  fileName = input("Enter file name:  ")
#   filePath = filePath + "\\" + fileName
#   print(filePath)
#   with open(filePath, "w+") as file:
#       fileContent = fileContent.decode()
#       print(fileContent)
#       file.write(fileContent)

#file_path_to_send = input("Enter file path to your file: ")
#file_to_send = input("Enter file name to send: ")

#file_to_send = file_path_to_send + "\\" + file_to_send

#filePath = input("Enter file path: ")


#with open(file_to_send, "rb") as bin_file:
   # fileContent = bin_file.read()
    #print(fileContent)

#if os.path.exists(filePath):
   # fileName = input("Enter fie name: ")
    #filePath = filePath + "\\" + fileName
#    with open(filePath, "wb+") as file:
      #  print(fileContent)
        #file.write(fileContent)


str1 = "this is the first half, "
str1 = str1.encode()
str2 = "this is the second half"
str2 = str2.encode()

bytes_arr = str1 + str2

print(bytes_arr)


ba = bytearray()
print(type(ba))