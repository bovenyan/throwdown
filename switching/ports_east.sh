ovs-vsctl add-br vBundle
# dataports
# ovs-vsctl add-port vBundle eth1
# ovs-vsctl add-port vBundle eth2
ovs-vsctl add-port vBundle eth3
ovs-vsctl add-port vBundle eth4

ovs-vsctl add-port vBundle eth5 -- set interface eth5 type=internal
ifconfig eth5 192.168.5.1 netmask 255.255.255.0
ovs-vsctl set interface eth5 mac=\"00:00:00:00:00:51\"
arp -s 192.168.5.2 00:00:00:00:00:51

ovs-vsctl add-port vBundle mEth1 -- set interface mEth1 type=internal
ovs-vsctl set interface mEth1 mac=\"00:00:00:00:00:11\"
ifconfig mEth1 192.168.6.1 netmask 255.255.255.0
arp -s 192.168.6.2 00:00:00:00:00:21

ovs-vsctl add-port vBundle mEth2 -- set interface mEth2 type=internal
ovs-vsctl set interface mEth2 mac=\"00:00:00:00:00:12\"
ifconfig mEth1 192.168.7.1 netmask 255.255.255.0
arp -s 192.168.6.2 00:00:00:00:00:22

ovs-vsctl add-port vBundle mEth3
ovs-vsctl add-port vBundle mEth4
