import sys
import dpkt
import socket

class MB():
    
    UNIT_ID = 1
    FNCODE_READ_DISCRETE_INPUTS = 2
    FNCODE_READ_COILS = 1
    FNCODE_WRITE_SINGLE_COIL = 5
    FNCODE_WRITE_MULTIPLE_COILS = 15
    FNCODE_READ_INPUT_REGISTERS = 4
    FNCODE_READ_MULTIPLE_HOLDING_REGISTERS = 3
    FNCODE_WRITE_SINGLE_HOLDING_REGISTER = 6
    FNCODE_WRITE_MULTIPLE_HOLDING_REGISTERS = 16
    
    WRITE_SINGLE_COIL_OFF = 0
    WRITE_SINGLE_COIL_ON = 0xFF00
    
    @staticmethod
    def fnCode2Str(fn):
        if fn == FNCODE_READ_DISCRETE_INPUTS:
            return "Read Discrete Inputs"
        if fn == FNCODE_READ_COILS:
            return "Read Coils"
        if fn == FNCODE_WRITE_SINGLE_COIL:
            return "Write Single Coil"
        if fn == FNCODE_WRITE_MULTIPLE_COILS:
            return "Write Multiple Coils"
        if fn == FNCODE_READ_INPUT_REGISTERS:
            return "Read Input Registers"
        if fn == FNCODE_READ_MULTIPLE_HOLDING_REGISTERS:
            return "Read Multiple Holding Registers"
        if fn == FNCODE_WRITE_SINGLE_HOLDING_REGISTER:
            return "Write Single Holding Register"
        if fn == FNCODE_WRITE_MULTIPLE_HOLDING_REGISTERS:
            return "Write Multiple Holding Registers"
    

class MBTransaction():
    
    def __init__(self, timestamp, buf):
        self.buf = b''
        self.time = timestamp
        self.valid = False
        self.len = 0
        self.wait_for_reply = False
        self.append(buf)
    
    def append(self, buf):
        self.buf += buf
        self.check()
    
    def check(self):
        if len(self.buf < 6): return
        self.len = int.from_bytes(recv_buf[4:6], byteorder='big', signed=False) + 6
        if len(self.buf) < self.len: return
        if len(self.buf) > self.len: print("Warning: Multiple transaction in single connection or transaction longer than expected!")
        self.tn = int.from_bytes(buf[0:2], byteorder='big', signed=False)
        self.fn = buf[7]
        self.valid = True
    
    def recv(self, sock):
        while True:
            msg = sock.recv(6 - len(recv_buf))
            if len(msg) == 0:
                print("No reply")
                break
            recv_buf.extend(msg)
            if len(recv_buf) == 6: break
        l = int.from_bytes(recv_buf[4:6], byteorder='big', signed=False) + 6
        while True:
            msg = sock.recv(l - len(recv_buf))
            if len(msg) == 0:
                print("No reply")
                break
            recv_buf.extend(msg)
            #print("%d bytes needed," % l, "%d bytes buffered" % len(recv_buf))
            if len(recv_buf) == l: break
    
    def send(self, ip, port=502):
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
    
        print(f"Sending {MB.fnCode2Str(self.fn)}...")
    
        i = 0
        while i < len(self.buf):
            i += self.sock.send(self.buf[i:])
        
        # Wait for the reply
        if self.wait_for_reply:
            recv_buf = bytearray()
            try:
                self.recv(s)
                s.shutdown(socket.SHUT_RDWR)
                print("Reply received.")
            except OSError as err:
                print("Failed:", err)
            s.close()
        else:
            print("Not waiting for reply.")

if len(sys.argv) < 5:
    print("Usage: python3 mbfilter.py <pcap_file_name> <pcap slave/server IP> <pcap master/client IP> <current server IP>")
    exit(-1)
    
PCAP_SERVER_IP = sys.argv[2]
PCAP_CLIENT_IP = sys.argv[3]
CURR_SERVER_IP = sys.argv[4]

fpcap = open(sys.argv[1], 'rb')
pcap = dpkt.pcap.Reader(fpcap)

flows = dict()
order = []
last = None

for timestamp, buf in pcap:
    eth = dpkt.ethernet.Ethernet(buf)
    if not isinstance(eth.data, dpkt.ip.IP):
        continue
    ip = eth.data
    if not isinstance(ip.data, dpkt.tcp.TCP):
        continue
    tcp = ip.data
    src_addr = socket.inet_ntop(socket.AF_INET, ip.src)
    dst_addr = socket.inet_ntop(socket.AF_INET, ip.dst)
    print(src_addr, tcp.sport, "->", dst_addr, tcp.dport)
    if src_addr == PCAP_CLIENT_IP and dst_addr == PCAP_SERVER_IP and tcp.dport == 502:
        if tcp.sport not in flows:
            flows[tcp.sport] = MBTransaction(timestamp, tcp.data)
            order.append(flows[tcp.sport])
            last = tcp.sport
        else:
            flows[tcp.sport].append(tcp.data)
            if last != tcp.sport: last = None
    elif dst_addr == PCAP_CLIENT_IP and tcp.dport in flows and src_addr == PCAP_SERVER_IP and tcp.sport == 502:
        flows[tcp.dport].wait_for_reply = (last == tcp.dport)
    
# order is sorted by timestamp (probably)
for pkt in order:
    pkt.send(CURR_SERVER_IP)