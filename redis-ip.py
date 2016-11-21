#!venv/bin/python
try:
    from redis import StrictRedis as Redis
except ImportError:
    # Old python-redis does not have StrictRedis
    from redis import Redis

import netaddr
import sys
import time

r = Redis()

v4subnetcache = dict()

def getfirstlast(key, score):
    res = r.zrangebyscore(key, score, 'inf', 0, 1, withscores=True, score_cast_func=int)
    if res:
        first, last = res[0]
        return int(first), int(last)

def storev4(subnet):
    subnet = netaddr.IPNetwork(subnet)
    r.zadd('ip4', subnet.last, '%s' % subnet.first)
    v4subnetcache[(subnet.first, subnet.last)] = subnet

def fetchv4(ip):
    ip = netaddr.IPAddress(ip)
    res = getfirstlast('ip4', int(ip))
    if res:
        first, last = res
        if int(ip) >= first:
            return first, last

subnets = [
    '192.0.2.0/24',
    '192.0.3.0/24',
    '192.0.4.0/24',
    '192.0.5.0/24',
    '192.0.6.0/24',
    # '192.0.2.0/28',
    '192.0.2.64/28',
    '192.0.2.240/28'
]

ips = [
    '192.0.1.0',
    '192.0.2.30',
    '192.0.2.250',
    '192.0.2.65',
    '192.0.2.88',
    '192.0.4.53',
]

r.delete('ip4')

for subnet in subnets:
    storev4(subnet)

for ip in ips:
    subnet = fetchv4(ip)
    if subnet:
        subnet = v4subnetcache[subnet]
    print("%s in %s" % (ip, subnet))

v6subnetcache = dict()

def combineparts(parts):
    total = 0
    for part in parts:
        total = (total << 32) + part

    return total

def splitparts(i):
    part4 = i & ((1<<32) - 1)
    part3 = (i >> 32) & ((1<<32) - 1)
    part2 = (i >> 64) & ((1<<32) - 1)
    part1 = (i >> 96) & ((1<<32) - 1)
    return (part1, part2, part3, part4)

def getthree(key, score):
    res = r.zrangebyscore(key, score, 'inf', 0, 1, withscores=True, score_cast_func=int)
    if res:
        val, score = res[0]
        first, second = val.split()
        return int(score), int(first), int(second)

def storev6(subnet):
    subnet = netaddr.IPNetwork(subnet)

    firstparts = splitparts(subnet.first)
    lastparts = splitparts(subnet.last)
    # print(subnet, i, part1, part2, part3, part4, (part1<<96)+(part2<<64)+(part3<<32)+part4)

    r.zadd(combineparts(lastparts[:3]), lastparts[3], "%s %s" % (combineparts(lastparts[:4]), combineparts(firstparts[:4])))
    r.zadd(combineparts(lastparts[:2]), lastparts[2], "%s %s" % (combineparts(lastparts[:3]), combineparts(firstparts[:3])))
    r.zadd(combineparts(lastparts[:1]), lastparts[1], "%s %s" % (combineparts(lastparts[:2]), combineparts(firstparts[:2])))
    r.zadd('ip6'                      , lastparts[0], "%s %s" % (combineparts(lastparts[:1]), combineparts(firstparts[:1])))
    v6subnetcache[(subnet.first, subnet.last)] = subnet

def fetchv6(ip):
    ip = netaddr.IPAddress(ip)
    i = int(ip)

    parts = splitparts(i)

    totalfirst = 0
    totallast = 0
    key = 'ip6'
    buildparts = []
    for i in range(len(parts)):
        res = getthree(key, parts[i])
        if not res:
            return
        partiallast, last, first = res
        if first > combineparts(parts[:i+1]):
            return

        key = last

    return (first, last)
    # a = getfirstlast('ip6', part1)
    # if(a):
    #     print("a", a)
    #     b = r.zrangebyscore(a[0][0], part2, 'inf', 0, 1, withscores=True, score_cast_func=int)

    #     if(b):
    #         # print("b", b)
    #         c = r.zrangebyscore(b[0][0], part3, 'inf', 0, 1, withscores=True, score_cast_func=int)

    #         if(c):
    #             # print("c", c)
    #             d = r.zrangebyscore(c[0][0], part4, 'inf', 0, 1, withscores=True, score_cast_func=int)
    #             print("x", ip, d)

subnets = [
    '2001:db8::/32',
    '2600::/16',
    '2001:db9:0:0:50:50:0:0/96',
    '2500::/15'
]

ips = [
    '2001:db8::1',
    '2600:15::2',
    '2600::1',
    '2001:db9:0:0:50:49::1',
    '2001:db9:0:0:50:50::1',
    '2001:db9:0:0:50:51::1',
    '2001:db8:ffff:ffff:ffff:ffff:ffff:ffff',
    '2001:db8:ffff:ffff:ffff:ffff:ffff:fffe',
    '2001:db8::0',
    '2500:5:5:5:5:5:5:5',
    '2501::',
    '2501:ffff:ffff:ffff:ffff:ffff:ffff:ffff',
    '2502::',
    '2502:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
    ]

r.delete('ip6')

for subnet in subnets:
    storev6(subnet)

for ip in ips:
    subnet = fetchv6(ip)
    if subnet:
        subnet = v6subnetcache[subnet]
    print("%s in %s" % (ip, subnet))
