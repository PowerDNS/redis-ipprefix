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

