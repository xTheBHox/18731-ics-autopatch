import socket
import threading 

CLIENT_IP = '10.1.1.1'
SERVER_IP = '10.1.2.1'
SERVER_PORT = 502

class MBReply():
    
    UNIT_ID = 1
    
    FNCODE_READ_DISCRETE_INPUTS = 2
    FNCODE_READ_COILS = 1
    FNCODE_WRITE_SINGLE_COIL = 5
    FNCODE_WRITE_MULTIPLE_COILS = 15
    FNCODE_READ_INPUT_REGISTERS = 4
    FNCODE_READ_MULTIPLE_HOLDING_REGISTERS = 3
    FNCODE_WRITE_SINGLE_HOLDING_REGISTER = 6
    FNCODE_WRITE_MULTIPLE_HOLDING_REGISTERS = 6
    
    def __init__(self, b):
        l = int.from_bytes(b[4:6], byteorder='big', signed=False) + 6
        if l != len(b):
            print("Warning: length mismatch")
        self,tn = b[0:2]
        self.fn = b[7]
        if fn == FNCODE_READ_COILS:
            bits = int.from_bytes(b[8:10], byteorder='big', signed=False) + 6
            size = ((bits - 1) // 8) + 1
            self.data = bytearray(size + 1)
            self.data[0] = size
            self.len = size + 3
        elif fn == FNCODE_READ_DISCRETE_INPUTS:
            pass
        
    def send(self, sock):
        b = bytearray(8)
        b[0:2] = self.tn.to_bytes(2, byteorder='big', signed=False)
        b[4:6] = (2 + self.len).to_bytes(2, byteorder='big', signed=False)
        b[6] = MBPkt.UNIT_ID.to_bytes
        b[7] = self.fn
        b = b + self.data
        i = 0 
        while i < len(b):
            i += sock.send(b[i:], len(b) - i)
    
def thread_fn(sock):
    buf = bytearray()
    while True:
        msg = sock.recv()
        if len(msg) == 0: break
        buf.extend(msg)
        if len(buf) < 6: continue
        l = int.from_bytes(buf[4:6], byteorder='big', signed=False) + 6
        if len(buf) < l: continue
        P = MBPkt(buf[:l])
        P.send()
        buf = buf[l:]
        
threads = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', SERVER_PORT))
s.setblocking(False)
s.listen()
while True:
    sock, addr = s.accept()
    sock.setblocking(True)
    th = threading.Thread(target=thread_fn, args=sock)
    threads.append(th)
    th.start()
    for th in threads:
        th.join(0)

