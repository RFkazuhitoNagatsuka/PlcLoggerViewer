# KV Host Link IF (UDP)
# Version 1.0
# 2024/5/17

import time
from socket import *
import struct
import datetime

BUFSIZE = 4096

class kvHostLink:
    addr = ()
    destfins = []
    srcfins = []
    port = 8501


    def __init__(self, host, port=8501, timeout=2, max_attempts=10):
        self.addr = (host, port)
        self.port = port
        self.timeout = timeout
        self.max_attempts = max_attempts


    def sendrecive(self, command):
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('', self.port))
        s.settimeout(self.timeout)
        attempts = 0

        while attempts < self.max_attempts:
            s.sendto(command, self.addr)
            try:
                rcvdata = s.recv(BUFSIZE)
                return rcvdata
            except timeout as e:
                print(f"Timeout occurred on attempt {attempts + 1}: {e}")
                attempts += 1
                time.sleep(0.5)
            except Exception as e:
                print(f"An error occurred on attempt {attempts + 1}: {e}")
                attempts += 1
                time.sleep(0.5)

        print("All retry attempts failed.")
        return None

    def reads(self, addresssuffix, num):
        rcv = self.sendrecive(('RDS ' + addresssuffix + ' ' + str(num) + '\r').encode())
        return rcv

## Sample Code
if __name__ == "__main__":

    kv = kvHostLink('192.168.100.50', 8501, 2, 10)  # インスタンス生成時にIPアドレス、ポート、タイムアウト、リトライ回数を指定

    while True:
        data = kv.reads('DM10300.U',3)
        if data:
            print(data.decode('utf-8').strip())
        time.sleep(0.2)
