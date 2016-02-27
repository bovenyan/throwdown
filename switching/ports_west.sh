ovs-vsctl add-br vBundle
# data ports
ovs-vsctl add-port vBundle eth1
ovs-vsctl add-port vBundle eth2
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
ifconfig mEth1 192.168.7.2 netmask 255.255.255.0
arp -s 192.168.7.1 00:00:00:00:00:72

ovs-vsctl add-port vBundle mEth3
ovs-vsctl add-port vBundle mEth4

# set dpid to be first dataport
sudo ovs-vsctl set bridge vBundle other_config:datapath-id=00:00:00:00:00:02
