from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4, tcp, udp, icmp
from ryu.lib.packet import ether_types
from multiprocessing import Process
from ryu.app import event_message
from time import sleep
import random
import copy

from health.db_conn import db_api
from health.pingMonitor import *
from health.health import *

import netifaces as nif

default_qos = 1

class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _EVENTS = [event_message.EventMessage]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.arptable = {}
        self.arptable["192.168.5.1"] = "00:00:00:00:00:51"
        self.arptable["192.168.5.2"] = "00:00:00:00:00:52"
        self.arptable["192.168.6.1"] = "00:00:00:00:00:61"
        self.arptable["192.168.6.2"] = "00:00:00:00:00:62"
        self.arptable["192.168.7.1"] = "00:00:00:00:00:71"
        self.arptable["192.168.7.2"] = "00:00:00:00:00:72"
        self.arptable["192.168.8.1"] = "00:00:00:00:00:81"
        self.arptable["192.168.8.2"] = "00:00:00:00:00:82"
        self.arptable["192.168.9.1"] = "00:00:00:00:00:91"
        self.arptable["192.168.9.2"] = "00:00:00:00:00:92"

        self.arptable["192.168.1.1"] = "00:50:56:8d:c8:c6"
        self.arptable["192.168.1.2"] = "00:50:56:8d:fd:63"
        self.arptable["192.168.2.1"] = "00:50:56:8d:aa:52"
        self.arptable["192.168.2.2"] = "00:50:56:8d:59:8b"
        self.arptable["192.168.3.1"] = "00:50:56:8d:6b:80"
        self.arptable["192.168.3.2"] = "00:50:56:8d:27:5e"
        self.arptable["192.168.4.1"] = "00:50:56:8d:2e:7c"
        self.arptable["192.168.4.2"] = "00:50:56:8d:df:4f"

        self.west_dpid = nif.ifaddresses('vBundle')[nif.AF_LINK][0]['addr']
        self.west_dpid = int(self.west_dpid.replace(':', ''), 16)

        self.datapaths = [None, None]

        self.path_info = []  # west, east, west/east port
        # TODO: add LSP 1 and LSP 2
        self.path_info.append(["192.168.1.2", "192.168.1.1", 1])
        self.path_info.append(["192.168.2.2", "192.168.2.1", 2])
        self.path_info.append(["192.168.3.2", "192.168.3.1", 3])
        self.path_info.append(["192.168.4.2", "192.168.4.1", 4])

        self.vBundle_info = ["192.168.5.2", "192.168.5.1", 5]

        self.measure_info = []
        self.measure_info.append(["192.168.6.2", "192.168.6.1", 6])
        self.measure_info.append(["192.168.7.2", "192.168.7.1", 7])
        self.measure_info.append(["192.168.8.2", "192.168.8.1", 8])
        self.measure_info.append(["192.168.9.2", "192.168.9.1", 9])


        #self.lsp_rules = []  # recording the associated flow for each lsp
        #self.lsp_rules.append({})  # [cookie : [rule]]
        #self.lsp_rules.append({})  # [cookie : [rule]]
        #self.lsp_rules.append({})  # [cookie : [rule]]
        #self.lsp_rules.append({})  # [cookie : [rule]]

        self.db = db_api()

        # triggers event listener after 10 second
        #self.measurement_process = [None, None, None, None]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        # default fwd everything to controller
        match = datapath.ofproto_parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, match, actions, 0, 0, 0)

        if dpid == self.west_dpid:    # record datapath
            self.datapaths[0] = datapath
        else:
            self.datapaths[1] = datapath

        print "default ready + " + str(dpid)

        if not (None in self.datapaths):  # ready
            self.add_block_public()
            print "preparing measurements"
            for mLsp in range(4):
                self.add_measure_rules(mLsp)
                #self.measurement_process[mLsp] = Process(target=monitor_process_callback,
                #                                         args=(self.measure_info[mLsp][1],
                #                                               mLsp))
                #self.measurement_process[mLsp].start()

            print "measurements setup done"

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        in_port = msg.match['in_port']

        if not eth:
            return

        # handle ip
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ip_pkt = pkt.get_protocol(ipv4.ipv4)

            if (None in self.datapaths):
                print "ignore ... ovs not ready"
                return

            # get healthest lsp
            if (ip_pkt.proto == 6):  # tcp
                print "received IP packet"
                tcp_pkt = pkt.get_protocol(tcp.tcp)
                # TODO: import qos
                #qos = db.check_registered_qos(6, tcp_pkt.src_port,
                #                                 tcp_pkt.dst_port)
                #if qos is None:
                #    qos = default_qos
                qos = 1
                allocated_lsp = cal_healthest(qos)
                self.handle_ip(datapath.id, ip_pkt.proto,
                               tcp_pkt.src_port, tcp_pkt.dst_port,
                               allocated_lsp)
                # commit_flow
                # ... .

            elif(ip_pkt.proto == 17):  # udp
                udp_pkt = pkt.get_protocol(udp.udp)
                # qos = db.check_registered_flow(17, udp_pkt.src_port,
                #                               udp_pkt.dst_port)
                qos = 1
                allocated_lsp = cal_healthest(qos)
                self.handle_ip(datapath.id, ip_pkt.proto,
                               udp_pkt.src_port, udp_pkt.dst_port,
                               allocated_lsp)

            else: # icmp
                allocated_lsp = cal_healthest(0)
                self.handle_ip(datapath.id, ip_pkt.proto, None, None,
                               allocated_lsp)

            self.packet_out(datapath, msg.data, in_port,
                            self.vBundle_info[2])

    def handle_ip(self, dpid, proto, sPort=None, dPort=None, lsp_id=0):
        if (sPort is None):
            cookie = random.randint(1,65535)
        else:
            cookie = sPort * 65536 + dPort

        # self.lsp_rules[lsp_id][cookie] = [dpid, proto, sPort, dPort]

        if (dpid == self.datapaths[0].id):  # in from west
            # handle west
            datapath = self.datapaths[0]
            nat_src = self.path_info[lsp_id][0]
            nat_dst = self.path_info[lsp_id][1]
            self.create_nat(datapath, self.vBundle_info[2],
                            self.path_info[lsp_id][2], nat_src, nat_dst,
                            proto, cookie, sPort, dPort, 10, 100)

            # handle east
            datapath = self.datapaths[1]
            nat_src = self.vBundle_info[0]
            nat_dst = self.vBundle_info[1]
            self.create_nat(datapath, self.path_info[lsp_id][2],
                            self.vBundle_info[2], nat_src, nat_dst,
                            proto, cookie, sPort, dPort, 10, 100)

        elif (dpid == self.datapaths[1].id):   # in from east
            # handle east
            datapath = self.datapaths[1]
            nat_src = self.path_info[lsp_id][1]
            nat_dst = self.path_info[lsp_id][0]
            self.create_nat(datapath, self.vBundle_info[2],
                            self.path_info[lsp_id][2], nat_src, nat_dst,
                            proto, cookie, sPort, dPort, 10, 100)

            # handle east
            datapath = self.datapaths[0]
            nat_src = self.vBundle_info[1]
            nat_dst = self.vBundle_info[0]
            self.create_nat(datapath, self.path_info[lsp_id][2],
                            self.vBundle_info[2], nat_src, nat_dst,
                            proto, cookie, sPort, dPort, 10, 100)

        print "flow ready, selected lsp: " + str(lsp_id)

    def add_flow(self, datapath, match, actions, cookie=0, idle_timeout=10, priority=100):
        ofproto = datapath.ofproto
        parser= datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, match=match,
            command=ofproto.OFPFC_ADD, idle_timeout=idle_timeout, hard_timeout=0,
            priority=priority, cookie=cookie, instructions=inst)
        datapath.send_msg(mod)

    def del_flow(self, cookie):
        datapath = self.datapaths[0]
        ofproto = datapath.ofproto
        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, cookie=cookie,
            command=ofproto.OFPFC_DELETE, out_port=ofproto.OFPP_ANY,
            out_group=ofproto.OFPG_ANY)
        datapath.send_msg(mod)

        datapath = self.datapaths[1]
        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, cookie=cookie,
            command=ofproto.OFPFC_DELETE, out_port=ofproto.OFPP_ANY,
            out_group=ofproto.OFPG_ANY)
        datapath.send_msg(mod)

    def add_measure_rules(self, lsp_id):
        cookie = 255  # cookie will be 0xff for measurement rules
        # west -> east
        datapath = self.datapaths[0]
        nat_src = self.path_info[lsp_id][0]
        nat_dst = self.path_info[lsp_id][1]
        self.create_nat(datapath, self.measure_info[lsp_id][2],
                        self.path_info[lsp_id][2], nat_src, nat_dst, 1,
                        cookie, None, None, 0, 50)

        datapath = self.datapaths[1]
        nat_src = self.measure_info[lsp_id][0]
        nat_dst = self.measure_info[lsp_id][1]
        self.create_nat(datapath, self.path_info[lsp_id][2],
                        self.measure_info[lsp_id][2], nat_src, nat_dst, 1,
                        cookie, None, None, 0, 50)

        # east -> west
        datapath = self.datapaths[1]
        nat_src = self.path_info[lsp_id][1]
        nat_dst = self.path_info[lsp_id][0]
        self.create_nat(datapath, self.measure_info[lsp_id][2],
                        self.path_info[lsp_id][2], nat_src, nat_dst, 1,
                        cookie, None, None, 0, 50)

        datapath = self.datapaths[0]
        nat_src = self.measure_info[lsp_id][1]
        nat_dst = self.measure_info[lsp_id][0]
        self.create_nat(datapath, self.path_info[lsp_id][2],
                        self.measure_info[lsp_id][2], nat_src, nat_dst, 1,
                        cookie, None, None, 0, 50)

    def add_block_public(self):
        cookie = 254
        datapath = self.datapaths[0]
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_src="10.10.2.227")
        actions = []
        self.add_flow(datapath, match, actions, cookie, 0, 1)
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_dst="10.10.2.227")
        actions = []
        self.add_flow(datapath, match, actions, cookie, 0, 1)

        datapath = self.datapaths[1]
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_src="10.10.2.207")
        actions = []
        self.add_flow(datapath, match, actions, cookie, 0, 1)
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_dst="10.10.2.207")
        actions = []
        self.add_flow(datapath, match, actions, cookie, 0, 1)

    print "measurement ready"

    def packet_out(self, datapath, data, in_port, out_port):
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=datapath.ofproto.OFP_NO_BUFFER,
            in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def create_nat(self, datapath, in_port, out_port, nat_src, nat_dst, proto,
                   cookie, sPort=None, dPort=None, time_out=0, priority=100):
        parser = datapath.ofproto_parser
        match = None
        if (sPort is None and dPort is None):
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                    ip_proto=proto, in_port=in_port)
        else:
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                    ip_proto=proto, tcp_src=sPort,
                                    tcp_dst=dPort, in_port=in_port)
        actions = [parser.OFPActionSetField(ipv4_src=nat_src),
                   parser.OFPActionSetField(eth_src=self.arptable[nat_src]),
                   parser.OFPActionSetField(ipv4_dst=nat_dst),
                   parser.OFPActionSetField(eth_dst=self.arptable[nat_dst]),
                   parser.OFPActionOutput(out_port)]
        self.add_flow(datapath, match, actions, cookie, time_out, priority)

