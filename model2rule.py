# -*- coding: utf-8 -*-

fTraffic = "traffic"
fModel = "model2"
fProto = "proto"
fRuleFormat = "ruleformat"

fRules = "rules"

fTraffic = open(fTraffic,"r")
fModel = open(fModel,"r")
fProto = open(fProto,"r")
fRuleFormat = open(fRuleFormat,"r")

fRules = open(fRules,"w")

traffic = fTraffic.readline()

# read the model



GROUPNAME = "modbus"
SERVER_IP = '[192.168.1.101,192.168.1.102,192.168.1.103,192.168.1.104,192.168.1.105,192.168.1.106]'
SERVER_PORT = '502'
CLIENT_IP = '192.168.1.100'
CLIENT_PORT = 'any'

class FSM():
    """This class represents the FSM read from model. It contains the states, initial state and transition matrix."""
    def __init__(self, states, transMatrix, initial):
        self.states = states
        self.transMatrix = transMatrix
        self.initial = initial
        self.proto = {}
        #check if initial state is in states
        if self.initial not in self.states:
            print("WARNING: Initial state not found.")
        else:
            self.init_id = self.states.index(initial)
        #check if matrix has correct dimensions
        if len(self.transMatrix) != len(self.states):
            print("WARNING: Invalid matrix size (# rows).")
        for i, row in enumerate(self.transMatrix):
            if len(row) != len(self.states):
                print(f"WARNING: Invalid matrix size (# cols in row {i}).")
        
    def __repr__(self):
    
        v = "\n".join(str(r) for r in self.transMatrix)
    
        return f'''\
States: {" ".join(self.states)}

Transitions:
{v}

Initial state: {self.initial}
'''
    
    def generateFlowbitsOptions(self, sid, tid):
        # Generate the flowbits rule to check if in state S
        if sid == self.init_id:
            s_bits = f'isnotset,any,{GROUPNAME}'
        else:
            s_bits = f'isset,{self.states[sid]},{GROUPNAME}'
        
        # Generate the flowbits rule to set state T
        if tid == self.init_id:
            t_bits = f'unset,all,{GROUPNAME}'
        else:
            t_bits = f'setx,{self.states[tid]},{GROUPNAME}'
            
        return f'flowbits:{s_bits};flowbits:{t_bits};'
        
    def readContent(self):
        """This function reads the protocol specifications and fill self.proto"""
        #self.proto: key - transition    value: content
        while True:
            line = fProto.readline()
            if (len(line) == 0):
                break
            line = line.rstrip('\n')
            contents = line.split(' - ')
            if (len(contents) < 2):
                print("WARNING: Protocol specification in the wrong format.")
                break
            self.proto[contents[0]] = contents[1]

    def generateContent(self, sid, tid): 
        content = ''
        for entry in self.proto:
            if entry in self.transMatrix[sid][tid]:
                content += self.proto[entry]
        return content

     
    def generateRule(self, sid, tid):
        content = self.generateContent(sid, tid)
        flowbits = self.generateFlowbitsOptions(sid, tid)
        
        #Assume transitions that contains read is query from client to server, transition that contains
        #response is from server to client
        if "Read" in self.transMatrix[sid][tid]:
            read = 1
            return f'allow tcp {CLIENT_IP} {CLIENT_PORT} -> {SERVER_IP} {SERVER_PORT} (flow:established;{content}{flowbits}tag:session,exclusive;)' 
        elif "Response" in self.transMatrix[sid][tid]:
            read = 0
            return f'allow tcp {SERVER_IP} {SERVER_PORT} -> {CLIENT_IP} {CLIENT_PORT} (flow:established;{content}{flowbits}tag:session,exclusive;)' 
        else:
            print("WARNING: Protocal specification in wrong format, cannot decide direction of flow.")
            return ''
    
    def generateAllRules(self):
        self.readContent()
        for sid, row in enumerate(self.transMatrix):
            for tid, v in enumerate(row):
                if v: 
                    print(self.generateRule(sid, tid))
        

def readModel(fModel):
    """This function reads the model file and generate a FSM class out of it.""" 
    states = []
    transMatrix = []

    while True:
        line = fModel.readline()
        if len(line) == 0:
            break
        line = line.rstrip('\n')
        if line == "states":
            nextline = fModel.readline()
            nextline = nextline.rstrip('\n')
            states = nextline.split(",")
            m = len(states)
            for i in range(m):
                transMatrix.append([""] * m)
        if line == "#initial":
            nextline = fModel.readline()
            nextline = nextline.rstrip('\n')
            initstate = nextline
        if line == "#transitions":
            nextline = fModel.readline()
            nextline = nextline.rstrip('\n')
            transitions = nextline.split(",")
            for text in transitions:	
                transition = text.split(">")
                s = transition[0]
                v = transition[1]
                t = transition[2]
                sid = states.index(s)
                tid = states.index(t)
                transMatrix[sid][tid] = v
    return FSM(states, transMatrix, initstate)
    
F = readModel(fModel)
print(F)
F.generateAllRules()
    
    


# fRules.write("allow tcp any any -> any 502 (flow:from_client,established; content:\"|03 00|\"; offset:5; depth:2; content:"|08 00 04|"; offset:7; depth:3; flowbits:readregreq,mobus; msg:"Modbus TCP - Read Register 3"; tag:session, exclusive;)\n")
# fRules.write("allow "+traffic+"(flow:from_client,established\n") 
#content:\"|03 00|\"; offset:5; depth:2; content:"|08 00 04|"; offset:7; depth:3; flowbits:readregreq,mobus; msg:"Modbus TCP - Read Register 3"; tag:session, exclusive;)\n")
