import socket
import random

CLIENT_IP = '192.168.1.100'
SERVER_IP = '192.168.1.104'
SERVER_PORT = 502

class MB():
    
    UNIT_ID = 1
    FNCODE_READ_DISCRETE_INPUTS = 2
    FNCODE_READ_COILS = 1
    FNCODE_WRITE_SINGLE_COIL = 5
    FNCODE_WRITE_MULTIPLE_COILS = 15
    FNCODE_READ_INPUT_REGISTERS = 4
    FNCODE_READ_MULTIPLE_HOLDING_REGISTERS = 3
    FNCODE_WRITE_SINGLE_HOLDING_REGISTER = 6
    FNCODE_WRITE_MULTIPLE_HOLDING_REGISTERS = 6

class MBPkt():

    transaction_number = random.randint(0, 0xFFFF)
    
    def __init__(self, fn_code, data):
        self.tn = MBPkt.transaction_number
        self.fn = fn_code
        self.data = data
        MBPkt.transaction_number = (MBPkt.transaction_number + 1) % 0xFFFF
        
    def send(self, sock):
        b = bytearray(8)
        b[0:2] = self.tn.to_bytes(2, byteorder='big', signed=False)
        b[4:6] = (len(self.data) + 2).to_bytes(2, byteorder='big', signed=False)
        b[6] = MB.UNIT_ID
        b[7] = self.fn
        b = b + self.data
        i = 0 
        while i < len(b):
            i += sock.send(b[i:], len(b) - i)
        
        # Wait for the reply
        recv_buf = bytearray()
        while True:
            msg = s.recv(256)
            print(''.join('{:02x}'.format(x) for x in msg))
            if len(msg) == 0: break
            recv_buf.extend(msg)
            if len(recv_buf) < 6: continue
            l = int.from_bytes(recv_buf[4:6], byteorder='big', signed=False) + 6
            print("%d bytes needed," % l, "%d bytes buffered" % len(recv_buf))
            break
        
    @staticmethod
    def ReadCoils(start, count):
        b = bytearray(4)
        b[0:2] = start.to_bytes(2, byteorder='big', signed=False)
        b[2:4] = count.to_bytes(2, byteorder='big', signed=False)
        return MBPkt(MB.FNCODE_READ_COILS, b)
        
    @staticmethod
    def ReadDiscreteInputs(start, count):
        b = bytearray(4)
        b[0:2] = start.to_bytes(2, byteorder='big', signed=False)
        b[2:4] = count.to_bytes(2, byteorder='big', signed=False)
        return MBPkt(MB.FNCODE_READ_DISCRETE_INPUTS, b)
        
    @staticmethod
    def ReadHoldingMultiple(start, count):
        b = bytearray(4)
        b[0:2] = start.to_bytes(2, byteorder='big', signed=False)
        b[2:4] = count.to_bytes(2, byteorder='big', signed=False)
        return MBPkt(MB.FNCODE_READ_MULTIPLE_HOLDING_REGISTERS, b)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, SERVER_PORT))

# This is the send loop
for i in range(1, 10):
    print("Sending ReadCoils...")
    P = MBPkt.ReadCoils(0, i).send(s)
    print("Sending ReadDiscreteInputs...")
    P = MBPkt.ReadDiscreteInputs(0, i).send(s)
    print("Sending ReadHoldingMultiple...")
    P = MBPkt.ReadHoldingMultiple(0, i).send(s)
s.close()