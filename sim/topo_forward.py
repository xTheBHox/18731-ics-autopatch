#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import Node
from mininet.link import Link, Intf
from mininet.util import dumpNodeConnections

class create_topo(Topo):

    def build(self, n=2):

        h1 = self.addHost( 'h1' , ip = '192.168.1.100')
        h2 = self.addHost( 'h2' , ip = '192.168.1.101')
        i1 = self.addHost( 'i1' , ip = '0.0.0.0')
        s1 = self.addSwitch( 's1' )

        self.addLink( h1,s1 )
        self.addLink( h2,s1 )
        self.addLink( i1,s1 )
        self.addLink( i1,s1 )
    

def start_cli():
    topo = create_topo()
    net = Mininet(topo=topo)
    net.start()
    dumpNodeConnections(net.hosts)
    s1, h1, h2, i1 = net.get('s1', 'h1', 'h2', 'i1')
    net.pingAll()
    h1.cmd('ethtool --offload h1-eth0 rx off tx off')
    h2.cmd('ethtool --offload h2-eth0 rx off tx off')
    h2.cmd('python3 modbus_server.py &')
    h1.cmd('tcpdump -i h1-eth0 -w h1_f.pcap &')
    h2.cmd('tcpdump -i h2-eth0 -w h2_f.pcap &')
    i1.cmd('tcpdump -i i1-eth0 -w snort_in.pcap &')
    i1.cmd('tcpdump -i i1-eth1 -w snort_out.pcap &')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    start_cli()
