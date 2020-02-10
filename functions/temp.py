import socket
import sys

host = 'www.baidu.com'
port = 80
s = None

res = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)[0]
print(res)
'''
af, sockettype, proto, canonname, sa = res[0]
print('af:', af)
print('sockettype', sockettype)
print('proto', proto)
print('cannonname', canonname)
print('sa', sa)
'''
