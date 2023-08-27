#!/usr/bin/env python
import threading,os
from queue import Queue
import time
import socket
import ipaddress
import nmap

nm = nmap.PortScanner()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_subnet_from_ip(local_ip):
    net = ipaddress.ip_network(local_ip+'/255.255.255.0', strict=False)
    return net

def get_subnet():
    return get_subnet_from_ip(get_local_ip())

def scan(IPRange):
    nm.scan(hosts=IPRange, arguments='-sP -PS22,3389')
    #for x in nm.all_hosts():
        #print(nm[x])
    #hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]
    hosts_list = [(x) for x in nm.all_hosts()]
    return hosts_list

print_lock = threading.Lock()

def isOpen(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(0.1)
    result = sock.connect_ex((hostname, port))
    sock.close()
    return result == 0

def ipScan(targets):
    livehosts = []
    for target in targets:
        #print("testing:",target)
        res = isOpen(target, 135)
        if res:
            print("live:",target)
            livehosts.append(target)
        #else:
        #    print("offline:"+target)
    return livehosts


def portscan(target,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        con = s.connect((target,port))
        with print_lock:
            print('open: [',target,':',port,']')
        con.close()
    except:
        pass

# The threader thread pulls an worker from the queue and processes it
def threader():
    while True:
        # gets an worker from the queue
        worker = q.get()
        portscan(worker[0],worker[1])

        # completed with the job
        q.task_done()

# Create the queue and threader 
q = Queue()

# how many threads are we going to allow for
for x in range(100):
     t = threading.Thread(target=threader)

     # classifying as a daemon, so they will die when the main dies
     t.daemon = True

     # begins, must come after daemon definition
     t.start()


#targets = [str(ip) for ip in ipaddress.IPv4Network('192.168.36.0/24')]
# scan available hosts on a subnet

def get_live_hosts(subnet):
    hosts_list = scan(str(subnet)) #'192.168.207.1/24'
    return hosts_list

#ports = range(1,10000)
def get_open_ports(hosts_list,ports_list):

# for each active scan, do a port scan for ports 1 - 6000
    start = time.time()
    for target in hosts_list:
        for port in ports_list:
            q.put([target,port])

    # wait until the thread terminates.
    q.join()