# MC Protocol Frame3E (UDP/IP)
# Version 1.0
# 2024/5/17

from socket import *
import struct

BUFSIZE = 4096

class MCProtcol3E:
    addr = ()

    def __init__(self, host, port,timeout=2, max_attempts=10):
        self.addr = host, port

    def offset(self, adr):
        moffset = [0] * 3

        mtype = adr[:2]
        if mtype == 'SB' or mtype == 'SW' or mtype == 'DX' or mtype == 'DY':
            address = int(adr[2:], 16)
            moffset = list((address).to_bytes(3,'little'))

        elif mtype == 'TS' or mtype == 'TC' or mtype == 'TN' or mtype == 'SS'\
                or mtype == 'SC' or mtype == 'SN' or mtype == 'CS' or mtype == 'CC'\
                or mtype == 'CN' or mtype == 'SM' or mtype == 'SD':
            address = int(adr[2:])
            moffset = list((address).to_bytes(3,'little'))

        if mtype == 'TS':
            deviceCode = 0xC1
        elif mtype == 'TC':
            deviceCode = 0xC0
        elif mtype == 'TN':
            deviceCode = 0xC2
        elif mtype == 'SS':
            deviceCode = 0xC7
        elif mtype == 'SC':
            deviceCode = 0xC6
        elif mtype == 'SN':
            deviceCode = 0xC8
        elif mtype == 'CS':
            deviceCode = 0xC4
        elif mtype == 'CC':
            deviceCode = 0xC3
        elif mtype == 'CN':
            deviceCode = 0xC5
        elif mtype == 'SB':
            deviceCode = 0xA1
        elif mtype == 'SW':
            deviceCode = 0xB5
        elif mtype == 'DX':
            deviceCode = 0xA2
        elif mtype == 'DY':
            deviceCode = 0xA3
        elif mtype == 'SM':
            deviceCode = 0x91
        elif mtype == 'SD':
            deviceCode = 0xA9
        else:
            mtype = adr[:1]
            if mtype == 'X' or mtype == 'Y' or mtype == 'B' or mtype == 'W':
                address = int(adr[1:], 16)
            else:
                address = int(adr[1:])
            moffset = list((address).to_bytes(3,'little'))

            if mtype == 'X':
                deviceCode = 0x9C
            elif mtype == 'Y':
                deviceCode = 0x9D
            elif mtype == 'M':
                deviceCode = 0x90
            elif mtype == 'L':
                deviceCode = 0x92
            elif mtype == 'F':
                deviceCode = 0x93
            elif mtype == 'V':
                deviceCode = 0x94
            elif mtype == 'B':
                deviceCode = 0xA0
            elif mtype == 'D':
                deviceCode = 0xA8
            elif mtype == 'W':
                deviceCode = 0xB4
            elif mtype == 'S':
                deviceCode = 0x98

        return deviceCode, moffset



    def mcpheader(self, cmd):
        ary = bytearray(11)
        requestdatalength = struct.pack("<H", len(cmd) + 2)

        ary[0] = 0x50                      # sub header
        ary[1] = 0x00
        ary[2] = 0x00                      # Network No.
        ary[3] = 0xFF                      # PC No.
        ary[4] = 0xFF                      # Request destination module i/o No.
        ary[5] = 0x03
        ary[6] = 0x00                      # Request destination module station No.
        ary[7] = requestdatalength[0]      # Request data length
        ary[8] = requestdatalength[1]
        ary[9] = 0x10                      # CPU monitoring timer
        ary[10] = 0x00

        return ary


    def reads(self, memaddr, readsize, unitOfBit = False):
        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(2)

        # MC Protocol
        cmd = bytearray(10)
        cmd[0] = 0x01                     # Read Command
        cmd[1] = 0x04
        if unitOfBit:
            cmd[2] = 0x01                 # Sub Command
            cmd[3] = 0x00
        else:
            cmd[2] = 0x00
            cmd[3] = 0x00

        deviceCode, memoffset = self.offset(memaddr)
        cmd[4] = memoffset[0]             # head device
        cmd[5] = memoffset[1]
        cmd[6] = memoffset[2]
        cmd[7] = deviceCode               # Device code

        rsize = struct.pack("<H", readsize)
        cmd[8] = rsize[0]                 # Number of device
        cmd[9] = rsize[1]

        senddata = self.mcpheader(cmd) + cmd
        s.sendto(senddata, self.addr)

        res = s.recv(BUFSIZE)
        if res[9] == 0 and res[10] == 0:
            data = res[11:]
            return self.toInt16(data)
        else:
            return None

    def toInt16(self, data):
        outdata = []
        arydata = bytearray(data)
        for idx in range(0, len(arydata), 2):
            tmpdata = arydata[idx:idx+2]
            outdata += (struct.unpack('<h',tmpdata))

        return outdata

## Sample Code
if __name__ == "__main__":

    # example
    # set IPAddress,Port
    mcp = MCProtcol3E('192.168.100.51', 1026)

    # words
    while True:
        data = mcp.reads('D0000', 3)
        print(data)
