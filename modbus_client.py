import socket
import random

CLIENT_IP = '10.1.1.1'
SERVER_IP = '10.1.2.1'
SERVER_PORT = 502

class MBPkt():

    transaction_number = random.randint(0, 0xFFFF)
    
    UNIT_ID = 1
    
    FNCODE_READ_DISCRETE_INPUTS = 2
    FNCODE_READ_COILS = 1
    FNCODE_WRITE_SINGLE_COIL = 5
    FNCODE_WRITE_MULTIPLE_COILS = 15
    FNCODE_READ_INPUT_REGISTERS = 4
    FNCODE_READ_MULTIPLE_HOLDING_REGISTERS = 3
    FNCODE_WRITE_SINGLE_HOLDING_REGISTER = 6
    FNCODE_WRITE_MULTIPLE_HOLDING_REGISTERS = 6
    
    def __init__(self, fn_code, l, data):
        self.tn = MBPkt.transaction_number
        self.len = l
        self.fn = fn_code
        self.data = data
        MBPkt.transaction_number = (MBPkt.transaction_number + 1) % 0xFFFF
        
    def send(self, sock):
        b = bytes(8)
        b[0:2] = self.tn.to_bytes(2, byteorder='big', signed=False)
        b[4:6] = self.len.to_bytes(2, byteorder='big', signed=False)
        b[6] = MBPkt.UNIT_ID.to_bytes
        b[7] = self.fn
        b = b + self.data
        i = 0 
        while i < len(b):
            i += sock.send(b[i:], len(b) - i)
        
    @staticmethod
    def ReadCoils(start, count):
        b = bytes(4)
        b[0:2] = start.to_bytes(2, byteorder='big', signed=False)
        b[2:4] = count.to_bytes(2, byteorder='big', signed=False)
        return MBPkt(FNCODE_READ_COILS, 8, b)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(SERVER_IP, SERVER_PORT)

# This is the send loop
for i in range(20):
    print("Sending ReadCoils...")
    P = MBPkt.ReadCoils()
    P.send(s)
    recv_buf = bytearray()
    while True:
        msg = sock.recv()
        if len(msg) == 0: break
        recv_buf.extend(msg)
        if len(recv_buf) < 6: continue
        l = int.from_bytes(recv_buf[4:6], byteorder='big', signed=False) + 6
        if len(recv_buf) < l: continue
        print("Reply received.")
        break