from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
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


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
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
        #self.path_info.append(["192.168.1.2", "192.168.1.1", 8])
        #self.path_info.append(["192.168.2.2", "192.168.2.1", 9])
        self.path_info.append(["192.168.3.2", "192.168.3.1", 1]) 
        self.path_info.append(["192.168.4.2", "192.168.4.1", 2])
        self.path_info.append(["192.168.3.2", "192.168.3.1", 1])
        self.path_info.append(["192.168.4.2", "192.168.4.1", 2])
        self.vBundle_info = ["192.168.5.2", "192.168.5.1", 2]

        self.measure_info = []
        self.measure_info.append(["192.168.6.2", "192.168.6.1", 4])
        self.measure_info.append(["192.168.7.2", "192.168.7.1", 5])
        self.measure_info.append(["192.168.8.2", "192.168.8.1", 6])
        self.measure_info.append(["192.168.9.2", "192.168.9.1", 7])

        self.lsp_rules = []  # recording the associated flow for each lsp
        self.lsp_rules.append({})  # [cookie : [rule]]
        self.lsp_rules.append({})  # [cookie : [rule]]

        self.db = db_api()

        # triggers event listener after 10 second
        self.measurement_process = [None, None, None, None]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        # default fwd everything to controller
        match = datapath.ofproto_parser.OFPMatch()
        actions = [datapath.ofproto_parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.add_flow(datapath, match, actions, 0, 0, 0)

        print dpid
        if dpid == self.west_dpid:    # record datapath
            self.datapaths[0] = datapath
        else:
            self.datapaths[1] = datapath

        print "default ready"

        if not (None in self.datapaths):  # ready
            #for lsp_id in range(4):
            #    self.add_measure_rules(lsp_id)
            mLsp = 2
            self.add_measure_rules(mLsp)
            print "preparing measurements"
            self.measurement_process[mLsp] = Process(target=monitor_process_callback,
                                               args=(self.measure_info[mLsp][1],
                                                     mLsp))
            self.measurement_process[mLsp].start()
            mLsp = 3
            self.add_measure_rules(mLsp)
            self.measurement_process[mLsp] = Process(target=monitor_process_callback,
                                               args=(self.measure_info[mLsp][1],
                                                     mLsp))
            self.measurement_process[mLsp].start()
            print "measurements setup done"

            # start a process to measure

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        in_port = msg.in_port

        if not eth:
            return

        # handle arp
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            print "Error; ARP received.... " + pkt.get_protocol(arp.arp)
            return 
            # pkt_arp = pkt.get_protocol(arp.arp)
            # self._handle_arp(datapath, in_port, eth, pkt_arp)

        # handle ip
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ip_pkt = pkt.get_protocol(ipv4.ipv4)
            return 
            if (None in self.datapaths):
                print "ignore ... ovs not ready"
                return

            # get healthest lsp
            if (ip_pkt.proto == 6):  # tcp
                tcp_pkt = pkt.get_protocol(tcp.tcp)
                qos = check_registered_flow(6, tcp_pkt.src_port,
                                            tcp_pkt.dst_port)
                allocated_lsp = cal_healthest(qos)
                self.handle_ip(datapath.id, ip_pkt.proto,
                               tcp_pkt.src_port, tcp_pkt.dst_port,
                               allocated_lsp)

            elif(ip_pkt.proto == 17):  # udp
                udp_pkt = pkt.get_protocol(udp.udp)
                qos = check_registered_flow(17, udp_pkt.src_port,
                                            udp_pkt.dst_port)
                self.handle_ip(datapath.id, ip_pkt.proto,
                               udp_pkt.src_port, udp_pkt.dst_port,
                               allocated_lsp)

            else: # icmp  
                allocated_lsp = cal_healthest(0)
                self.handle_ip(datapath.id, ip_pkt.proto, None, None,
                               allocated_lsp)

            self.packet_out(datapath, msg.data, msg.in_port,
                            self.vBundle_info[2])

    def lsp_failover(self, ev):
        print ev.message
        print "start deleting + new: " + str(ev[0])
        print self.lsp_rules
        for cookie in self.lsp_rules[ev[0]]:
            print cookie
            self.del_flow(cookie)

            orig_rule = self.lsp_rules[ev.orig_lsp][cookie]
            print orig_rule
            self.handle_ip(orig_rule[0], orig_rule[1], orig_rule[2],
                           orig_rule[3], ev[1])

        self.lsp_rules[ev[0]].clear()

    def flow_migration(self, cookie, orig_lsp, new_lsp):
        self.del_flow(cookie)
        orig_rule = self.lsp_rules[orig_lsp]
        self.handle_ip(orig_rule[0], orig_rule[1], orig_rule[2],
                       orig_rule[3], new_lsp)
        del self.lsp_rules[cookie]

    def handle_ip(self, dpid, proto, sPort=None, dPort=None, lsp_id=0):
        if (sPort is None):
            cookie = random.randint(1,65535)
        else:
            cookie = sPort * 65536 + dPort
        
        self.lsp_rules[lsp_id][cookie] = [dpid, proto, sPort, dPort]
        print self.lsp_rules

        if (dpid == self.datapaths[0]):  # in from west
            # handle west
            datapath = self.datapaths[0]
            parser = datapath.ofproto_parser
            match = parser.OFPMatch(dl_type=ether_types.ETH_TYPE_IP,
                                    nw_proto=proto, tp_src=sPort,
                                    tp_dst=dPort, in_port=self.vBundle_info[2])
            
            nat_src = self.path_info[lsp_id][0]
            nat_dst = self.path_info[lsp_id][1]
            actions = [parser.OFPActionSetNwSrc(nat_src),
                       parser.OFPActionSetDlSrc(self.arptable[nat_src]),
                       parser.OFPActionSetNwDst(nat_dst),
                       parser.OFPActionSetDlDst(self.arptable[nat_dst]),
                       parser.OFPActionOutput(self.path_info[lsp_id][2])]

            self.add_flow(datapath, match, actions, cookie)

            # handle east
            datapath = self.datapaths[1]
            parser = datapath.ofproto_parser
            match = parser.OFPMatch(dl_type=ether_types.ETH_TYPE_IP,
                                    nw_proto=proto, tp_src=sPort,
                                    tp_dst=dPort, in_port=self.path_info[lsp_id][2])

            nat_src = self.vBundle_info[0]
            nat_dst = self.vBundle_info[1]
            actions = [parser.OFPActionSetNwSrc(nat_src),
                       parser.OFPActionSetDlSrc(self.arptable[nat_src]),
                       parser.OFPActionSetNwDst(nat_dst),
                       parser.OFPActionSetDlDst(self.arptable[nat_dst]),
                       parser.OFPActionOutput(self.vBundle_info[2])]
            
            self.add_flow(datapath, match, actions, cookie)

        elif (dpid == self.datapaths[1]):   # in from east
            # handle east
            datapath = self.datapaths[1]
            parser = datapath.ofproto_parser
            match = parser.OFPMatch(dl_type=ether_types.ETH_TYPE_IP,
                                    nw_proto=proto, tp_src=sPort,
                                    tp_dst=dPort, in_port=self.vBundle_info[2])

            nat_src = self.path_info[lsp_id][1]
            nat_dst = self.path_info[lsp_id][0]
            actions = [parser.OFPActionSetNwSrc(nat_src),
                       parser.OFPActionSetDlSrc(self.arptable[nat_src]),
                       parser.OFPActionSetNwDst(nat_dst),
                       parser.OFPActionSetDlDst(self.arptable[nat_dst]),
                       parser.OFPActionOutput(self.path_info[lsp_id][2])]

            self.add_flow(datapath, match, actions, cookie)

            # handle east
            datapath = self.datapaths[0]
            parser = datapath.ofproto_parser
            match = parser.OFPMatch(dl_type=ether_types.ETH_TYPE_IP,
                                    nw_proto=proto, tp_src=sPort,
                                    tp_dst=dPort, in_port=self.path_info[lsp_id][2])

            nat_src = self.vBundle_info[1]
            nat_dst = self.vBundle_info[0]
            actions = [parser.OFPActionSetNwSrc(nat_src),
                       parser.OFPActionSetDlSrc(self.arptable[nat_src]),
                       parser.OFPActionSetNwDst(nat_dst),
                       parser.OFPActionSetDlDst(self.arptable[nat_dst]),
                       parser.OFPActionOutput(self.vBundle_info[2])]

            self.add_flow(datapath, match, actions, cookie)

        print "flow ready"

    def add_flow(self, datapath, match, actions, cookie=0, idle_timeout=10, priority=100):
        ofproto = datapath.ofproto
        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=priority,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions, cookie=cookie)
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
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(dl_type=ether_types.ETH_TYPE_IP,
                                nw_proto=1,
                                in_port=self.measure_info[lsp_id][2])

        nat_src = self.path_info[lsp_id][0]
        nat_dst = self.path_info[lsp_id][1]
        actions = [parser.OFPActionSetNwSrc(nat_src),
                   parser.OFPActionSetDlSrc(self.arptable[nat_src]),
                   parser.OFPActionSetNwDst(nat_dst),
                   parser.OFPActionSetDlDst(self.arptable[nat_dst]),
                   parser.OFPActionOutput(self.path_info[lsp_id][2])]

        self.add_flow(datapath, match, actions, cookie, 0, 50)

        datapath = self.datapaths[1]
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(dl_type=ether_types.ETH_TYPE_IP,
                                nw_proto=1,
                                in_port=self.path_info[lsp_id][2])
        
        nat_src = self.measure_info[lsp_id][0]
        nat_dst = self.measure_info[lsp_id][1]
        actions = [parser.OFPActionSetNwSrc(nat_src),
                   parser.OFPActionSetDlSrc(self.arptable[nat_src]),
                   parser.OFPActionSetNwDst(nat_dst),
                   parser.OFPActionSetDlDst(self.arptable[nat_dst]),
                   parser.OFPActionOutput(self.measure_info[lsp_id][2])]
        
        self.add_flow(datapath, match, actions, cookie, 0, 50)

        # east -> west
        datapath = self.datapaths[1]
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(dl_type=ether_types.ETH_TYPE_IP,
                                nw_proto=1,
                                in_port=self.measure_info[lsp_id][2])

        nat_src = self.path_info[lsp_id][1]
        nat_dst = self.path_info[lsp_id][0]
        actions = [parser.OFPActionSetNwSrc(nat_src),
                   parser.OFPActionSetDlSrc(self.arptable[nat_src]),
                   parser.OFPActionSetNwDst(nat_dst),
                   parser.OFPActionSetDlDst(self.arptable[nat_dst]),
                   parser.OFPActionOutput(self.path_info[lsp_id][2])]

        self.add_flow(datapath, match, actions, cookie, 0, 50)

        datapath = self.datapaths[0]
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(dl_type=ether_types.ETH_TYPE_IP,
                                nw_proto=1,
                                in_port=self.path_info[lsp_id][2])
        
        nat_src = self.measure_info[lsp_id][1]
        nat_dst = self.measure_info[lsp_id][0]
        actions = [parser.OFPActionSetNwSrc(nat_src),
                   parser.OFPActionSetDlSrc(self.arptable[nat_src]),
                   parser.OFPActionSetNwDst(nat_dst),
                   parser.OFPActionSetDlDst(self.arptable[nat_dst]),
                   parser.OFPActionOutput(self.measure_info[lsp_id][2])]
        
        self.add_flow(datapath, match, actions, cookie, 0, 50)

    print "measurement ready"

    def packet_out(self, datapath, data, in_port, out_port):
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=datapath.ofproto.OFP_NO_BUFFER,
            in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    """
    def _handle_arp(self, datapath, port, eth, pkt_arp):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if pkt_arp.opcode != arp.ARP_REQUEST:
            return
        pkt = packet.Packet()

        if pkt_arp.dst_ip in self.arptable:
           fin_src_mac = self.arptable[pkt_arp.dst_ip]

        pkt.add_protocol(ethernet.ethernet(ethertype=eth.ethertype, dst=eth.src,
                                           src=fin_src_mac))
        pkt.add_protocol(arp.arp(opcode=arp.ARP_REPLY,
                                 src_mac=fin_src_mac, src_ip=pkt_arp.dst_ip,
                                 dst_mac=eth.src, dst_ip=pkt_arp.src_ip))
        pkt.serialize()
        data = pkt.data
        actions = [parser.OFPActionOutput(port=port)]
        self.logger.info("packet out for arp reply %s" %(pkt,))

        out = parser.OFPPacketOut( datapath=datapath,
                                   buffer_id=ofproto.OFP_NO_BUFFER,
                                   in_port = ofproto.OFPP_CONTROLLER,
                                   actions=actions, data=data)
        datapath.send_msg(out)
    """
