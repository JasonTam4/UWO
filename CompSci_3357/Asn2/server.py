# to run in terminal: python server.py
from chatroom import (ServerTCP, ServerUDP)

server = ServerUDP(12345)
server.run()
