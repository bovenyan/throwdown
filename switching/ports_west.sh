ovs-vsctl add-br vBundle
# data ports
#ovs-vsctl add-port vBundle eth1
#ovs-vsctl add-port vBundle eth2
ovs-vsctl add-port vBundle eth3
ovs-vsctl add-port vBundle eth4

# app ports
ovs-vsctl add-port vBundle eth5 -- set interface eth5 type=internal
ifconfig eth5 192.168.5.2 netmask 255.255.255.0
ovs-vsctl set interface eth5 mac=\"00:00:00:00:00:52\"
arp -s 192.168.5.1 00:00:00:00:00:52

# measure ports
ovs-vsctl add-port vBundle mEth1 -- set interface mEth1 type=internal
ovs-vsctl set interface mEth1 mac=\"00:00:00:00:00:62\"
ifconfig mEth1 192.168.6.2 netmask 255.255.255.0
arp -s 192.168.6.1 00:00:00:00:00:62

ovs-vsctl add-port vBundle mEth2 -- set interface mEth2 type=internal
ovs-vsctl set interface mEth2 mac=\"00:00:00:00:00:72\"
ifconfig mEth2 192.168.7.2 netmask 255.255.255.0
arp -s 192.168.7.1 00:00:00:00:00:72

ovs-vsctl add-port vBundle mEth3 -- set interface mEth3 type=internal
ovs-vsctl set interface mEth3 mac=\"00:00:00:00:00:82\"
ifconfig mEth3 192.168.8.2 netmask 255.255.255.0
arp -s 192.168.8.1 00:00:00:00:00:82

ovs-vsctl add-port vBundle mEth4 -- set interface mEth4 type=internal
ovs-vsctl set interface mEth4 mac=\"00:00:00:00:00:92\"
ifconfig mEth4 192.168.9.2 netmask 255.255.255.0
arp -s 192.168.9.1 00:00:00:00:00:92

# set dpid to be first dataport
ovs-vsctl set bridge vBundle other_config:datapath-id=00:00:00:00:00:02

# verify settings
ovs-ofctl show vBundle
arp -n | grep CM
