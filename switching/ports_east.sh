ovs-vsctl add-br vBundle
# dataports
# ovs-vsctl add-port vBundle eth1
# ovs-vsctl add-port vBundle eth2
ovs-vsctl add-port vBundle eth3
ovs-vsctl add-port vBundle eth4

# app ports
ovs-vsctl add-port vBundle eth5 -- set interface eth5 type=internal
ifconfig eth5 192.168.5.1 netmask 255.255.255.0
ovs-vsctl set interface eth5 mac=\"00:00:00:00:00:51\"
arp -s 192.168.5.2 00:00:00:00:00:51

# measure ports
ovs-vsctl add-port vBundle mEth1 -- set interface mEth1 type=internal
ovs-vsctl set interface mEth1 mac=\"00:00:00:00:00:61\"
ifconfig mEth1 192.168.6.1 netmask 255.255.255.0
arp -s 192.168.6.2 00:00:00:00:00:61

ovs-vsctl add-port vBundle mEth2 -- set interface mEth2 type=internal
ovs-vsctl set interface mEth2 mac=\"00:00:00:00:00:71\"
ifconfig mEth2 192.168.7.1 netmask 255.255.255.0
arp -s 192.168.7.2 00:00:00:00:00:72

ovs-vsctl add-port vBundle mEth3 -- set interface mEth3 type=internal
ovs-vsctl set interface mEth3 mac=\"00:00:00:00:00:81\"
ifconfig mEth3 192.168.8.1 netmask 255.255.255.0
arp -s 192.168.8.2 00:00:00:00:00:81

ovs-vsctl add-port vBundle mEth4 -- set interface mEth4 type=internal
ovs-vsctl set interface mEth4 mac=\"00:00:00:00:00:91\"
ifconfig mEth4 192.168.9.1 netmask 255.255.255.0
arp -s 192.168.9.2 00:00:00:00:00:91

# set dpid to be first dataport
ovs-vsctl set bridge vBundle other_config:datapath-id=00:00:00:00:00:02

# verify settings
ovs-ofctl show vBundle
arp -n | grep CM
