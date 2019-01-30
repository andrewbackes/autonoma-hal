#!/usr/bin/env python3

import logging
import socket

logger = logging.getLogger(__name__)


class TCP:
    bind_ip = '0.0.0.0'
    bind_port = 9091
    conn_buffer_size = 4096

    def __init__(self):
        logger.setLevel(logging.DEBUG)
        self.conn = None

    def send(self, msg):
        if self.conn:
            print("Sending " + msg)
            self.conn.sendall((msg + '\n').encode())
        else:
            print("Not connected. Can not send.")

    def listen(self, handler):
        print(
            "Listening for TCP/IP connections on port ", self.bind_port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.bind_ip, self.bind_port))
        s.listen(1)
        exit = False
        while True:
            try:
                self.conn, addr = s.accept()
                print('Connection address: ' + addr[0])
                smsg = ""
                while True:
                    buffer = self.conn.recv(self.conn_buffer_size)
                    smsg += str(buffer, "utf-8")
                    # print("Received " + str(buffer, "utf-8"))
                    if not buffer:
                        break
                    cmds = smsg.split('\n')
                    if smsg.endswith('\n'):
                        smsg = ''
                    else:
                        smsg = cmds[-1]
                        cmds = cmds[:-1]
                    for cmd in cmds:
                        if cmd:
                            handler(cmd)
            except KeyboardInterrupt:
                print("User exit.")
                exit = True
                break
            if exit:
                break
        if self.conn:
            self.conn.close()
            self.conn = None
            s.close()
            print("Connection closed.")
