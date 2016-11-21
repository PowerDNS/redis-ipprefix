#!venv/bin/python
try:
    from redis import StrictRedis as Redis
except ImportError:
    # Old python-redis does not have StrictRedis
    from redis import Redis

import netaddr

r = Redis()

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

r.delete('ip')

for subnet in subnets:
    subnet = netaddr.IPNetwork(subnet)
    r.zadd('ip', subnet.last, "%03d %s" % (32-subnet.prefixlen, str(subnet)))

for ip in ips:
    ip = netaddr.IPAddress(ip)
    res = r.zrangebyscore('ip', int(ip), 'inf', 0, 1)
    print(ip, res)



subnets = [
    '2001:db8::/32',
    '2600::/16',
    '2001:db9:0:0:50:50:0:0/96'
]

ips = [
    '2001:db8::1',
    '2600:15::2',
    '2600::1',
    '2001:db9:0:0:50:49::1',
    '2001:db9:0:0:50:50::1',
    '2001:db9:0:0:50:51::1',
    ]

for subnet in subnets:
    subnet = netaddr.IPNetwork(subnet)
    i = subnet.last
    part4 = i & ((1<<32) - 1)
    part3 = (i >> 32) & ((1<<32) - 1)
    part2 = (i >> 64) & ((1<<32) - 1)
    part1 = (i >> 96) & ((1<<32) - 1)

    print(subnet, i, part1, part2, part3, part4, (part1<<96)+(part2<<64)+(part3<<32)+part4)

    r.zadd('%s%s%s' % (part1, part2, part3), part4, str(subnet))
    r.zadd('%s%s'   % (part1, part2)       , part3, '%s%s%s' % (part1, part2, part3))
    r.zadd('%s'     % (part1)              , part2, '%s%s'   % (part1, part2))
    r.zadd('ipv6'                          , part1, '%s'     % (part1))

for ip in ips:
    ip = netaddr.IPAddress(ip)
    i = int(ip)
    part4 = i & ((1<<32) - 1)
    part3 = (i >> 32) & ((1<<32) - 1)
    part2 = (i >> 64) & ((1<<32) - 1)
    part1 = (i >> 96) & ((1<<32) - 1)

    a = r.zrangebyscore('ipv6', part1, 'inf', 0, 1)
    if(a):
        # print("a", a)
        b = r.zrangebyscore(a[0], part2, 'inf', 0, 1)

        if(b):
            # print("b", b)
            c = r.zrangebyscore(b[0], part3, 'inf', 0, 1)

            if(c):
                # print("c", c)
                d = r.zrangebyscore(c[0], part4, 'inf', 0, 1)
                print(ip, d[0])