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
		print states
		m = len(states)
		for i in range(m):
			transMatrix.append(["null"]*m)
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
print transMatrix


# fRules.write("allow tcp any any -> any 502 (flow:from_client,established; content:\"|03 00|\"; offset:5; depth:2; content:"|08 00 04|"; offset:7; depth:3; flowbits:readregreq,mobus; msg:"Modbus TCP - Read Register 3"; tag:session, exclusive;)\n")
# fRules.write("allow "+traffic+"(flow:from_client,established\n") 
#content:\"|03 00|\"; offset:5; depth:2; content:"|08 00 04|"; offset:7; depth:3; flowbits:readregreq,mobus; msg:"Modbus TCP - Read Register 3"; tag:session, exclusive;)\n")
