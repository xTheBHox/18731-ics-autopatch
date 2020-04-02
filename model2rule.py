# -*- coding: utf-8 -*-

fTraffic = "traffic"
fModel = "model"
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
SERVER_IP = 'any'
SERVER_PORT = '502'
CLIENT_IP = 'any'
CLIENT_PORT = 'any'

class FSM():
    
    
    def __init__(self, states, transMatrix, initial):
        self.states = states
        self.transMatrix = transMatrix
        self.initial = initial
        if self.initial not in self.states:
            print("WARNING: Initial state not found.")
        else:
            self.init_id = self.states.index(initial)
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
        
    def generateContent(self, sid, tid): # maybe different args?
        # TODO @ Cindy
        return ''
     
    def generateRule(self, sid, tid):
        
        content = self.generateContent(sid, tid)
        flowbits = self.generateFlowbitsOptions(sid, tid)
        
        # need to figure out arrow directions
        return f'allow tcp {SERVER_IP} {SERVER_PORT} -> {CLIENT_IP} {CLIENT_PORT} (flow:established;{content}{flowbits}tag:session,exclusive;)' 
    
    def generateAllRules(self):
        for sid, row in enumerate(self.transMatrix):
            for tid, v in enumerate(row):
                if v: print(self.generateRule(sid, tid))
        

def readModel(fModel):

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
