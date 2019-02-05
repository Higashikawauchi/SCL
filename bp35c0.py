# coding: utf-8
# 2018.04.03
import time


class commands:
    CR = "\r"
    LF = "\n"
    CRLF = CR+LF

    # ヘルパかんすう
    def getHead(self, str):
        items = str.split()
        if len(items) > 0:
            return items[0]
        else:
            return ""

            # コンストラクタ
    def __init__(self, seri):
        self.ser = seri

    def settimeout(self, time):
        self.ser.timeout = time

    def gettimeout(self):
        return self.ser.timeout

    def write(self, str):
        self.ser.write(str + self.CRLF)

    def read(self, *args):
        return self.ser.read(*args)

    def readline(self, timeout=None):
        self.ser.timeout = timeout
        res = self.ser.readline()
        if res.startswith("ERXUDP"):
            items = res.split(' ', 9)
            datalen = items[8]
            data = " ".join(items[9:])
            data_length = int(datalen, 16) + 2
            read_length = len(data)
            if data_length > read_length:
                res = res + self.ser.read(data_length-read_length)
        return res.strip()

    def readall(self):
        res = ""
        c = ser.read()
        while len(c) > 0:
            res = res + c
        return res

    def readTo(self, end):
        res = ""
        c = self.ser.read()
        while len(c) != 0 and c != end:
            res = res + c
            c = self.ser.read()
        return res

    def readBytes(self, length):
        return self.ser.read(length)

    def getSKSREG(self, sreg):
        cmd = "SKSREG " + sreg
        self.write(cmd)
        res = self.ser.readline()
        head = self.getHead(res)
        okey = ""
        while head not in ["OK", "ESREG", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
            if head == "ESREG":
                okey = self.ser.readline()
            elif head == "OK":
                res = ""
                okey = head
                break
        return cmd, res, okey

    def setSKSREG(self, sreg, val):
        cmd = "SKSREG " + sreg + " " + val
        self.write(cmd)

        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKSREG(self, reg, val=None):
        if val is None:
            return self.getSKSREG(reg)
        else:
            return self.setSKSREG(reg, val)

    def WAKE(self):
        cmd = "a"
        self.write(cmd)
        res = self.readline(5)
        head = self.getHead(res)
        while head not in ["FAIL", "EVENT"]:
            res = self.ser.readline()
            if len(res) == 0:
                self.write(cmd)
            head = self.getHead(res)
        return cmd, res

    def SKINFO(self):
        cmd = "SKINFO"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while len(res) > 0 and not res.split()[0] in ["EINFO", "FAIL"]:
            res = self.readline()
            head = self.getHead(res)
        okey = self.readline()
        return cmd, res, okey

    def SKSTART(self):
        cmd = "SKSTART"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKJOIN(self, ipv6):
        self.join_completed = False
        self.joined = False
        cmd = "SKJOIN " + ipv6
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKREJOIN(self):
        cmd = "SKREJOIN"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKTERM(self):
        cmd = "SKTERM"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKJOINFOR(self, ipv6):
        cmd = "SKJOINFOR " + ipv6
        self.write(cmd)
        res = self.readline()
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKTERMFOR(self, ipv6):
        cmd = "SKTERMFOR " + ipv6
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKSENDTO(self, handle, ipv6, port, sec, side, data, datalen=None):
        data = bytes(data)
        if datalen is None:
            datalen = "%04X" % len(data)
        length = int(datalen, 16)
        if len(data) != length:
            raise ValueError("データ長とデータの長さが違う")
        if len(data) > 1232:
            raise ValueError("データが長すぎる")
        items = ["SKSENDTO", handle, ipv6, port, sec, side, datalen]
        cmd = " ".join(items)
        self.ser.write(cmd)
        self.ser.write(" ")
        self.ser.write(data)

        # self.ser.write(self.CRLF) とするとechobackが入る
        starttime = time.time()
        res = self.ser.readline()
        head = self.getHead(res)
        interval = time.time() - starttime
        while head not in ["OK", "FAIL"]:
            starttime = time.time()
            res = self.ser.readline()
            head = self.getHead(res)
            interval = time.time() - starttime

        return cmd, res

    def SKPING(self, side, ipv6):
        cmd = "SKPING " + side + " " + ipv6
        self.write(cmd)
        res = self.ser.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKSCAN(self, mode, mask, duration, side):
        self.scan_completed = False
        items = ["SKSCAN", mode, mask, duration, side]
        cmd = " ".join(items)
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)

        return cmd, res

    def SKRMDEV(self, targetMac):
        cmd = "SKRMDEV "+targetMac
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKAUTOUPD(self):
        cmd = "SKAUTOUPD"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKABORTUPD(self):
        cmd = "SKABORTUPD"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKOPEN(self, duration):
        cmd = "SKOPEN " + duration
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKSETPSK(self, len, key):
        items = ["SKSETPSK", len, key]
        cmd = " ".join(items)
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKSETPWD(self, pwd, length=None):
        if length is None:
            length = "%X" % len(pwd)
        items = ["SKSETPWD", length, pwd]
        cmd = " ".join(items)
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKSETHPWD(self, ipv6, pwd):
        items = ["SKSETHPWD", ipv6, pwd]
        cmd = " ".join(items)
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKSETRBID(self, id):
        cmd = "SKSETRBID "+id
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKADDNBR(self, ipv6, targetMac):
        items = ["SKADDNBR", ipv6, targetMac]
        cmd = " ".join(items)
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKUDPPORT(self, handle, port):
        items = ["SKUDPPORT", handle, port]
        cmd = " ".join(items)
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKSAVE(self):
        cmd = "SKSAVE"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKLOAD(self):
        cmd = "SKLOAD"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKERASE(self):
        cmd = "SKERASE"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKVER(self):
        cmd = "SKVER"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["EVER", "OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        if head == "EVER":
            okey = self.ser.readline()
        return cmd, res, okey

    def SKRESET(self):
        cmd = "SKRESET"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKTABLE(self, mode):
        cmd = "SKTABLE " + mode
        self.write(cmd)
        res = self.readline(1)
        head = self.getHead(res)
        while head not in ["EADDR", "ENEIGHBOR", "ENBR", "ESEC", "EPORT",
                           "OK", "FAIL"]:
            res = self.ser.readline(1)
            head = self.getHead(res)

        eventlines = []
        while head not in ["OK", "FAIL"]:
            eventlines.append(res.strip())
            res = self.readline()
            head = self.getHead(res)
        return cmd, "\r\n".join(eventlines), res

    def SKDSLEEP(self):
        cmd = "SKDSLEEP"
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKRFLO(self, mode):
        cmd = "SKRFLO " + mode
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.ser.readline()
            head = self.getHead(res)
        return cmd, res

    def SKLL64(self, mac):
        cmd = "SKLL64 " + mac
        self.write(cmd)
        res = self.readline()
        head = self.getHead(res)
        if head == "SKLL64":
            res = self.readline()
        return cmd, res

    def WOPT(self, mode):
        cmd = "WOPT " + mode + self.CR
        self.ser.write(cmd)
        res = self.readTo(self.CR)
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.readTo(self.CR)
            head = self.getHead(res)
        return cmd, res

    def ROPT(self):
        cmd = "ROPT " + self.CR
        self.ser.write(cmd)
        res = self.readTo("\r")
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.readTo(self.CR)
            head = self.getHead(res)
        return cmd, res

    def WUART(self, mode):
        cmd = "WUART " + mode + self.CR
        self.ser.write(cmd)
        res = self.readTo(self.CR)
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.readTo(self.CR)
            head = self.getHead(res)
        return cmd, res

    def RUART(self):
        cmd = "RUART" + self.CR
        self.ser.write(cmd)
        res = self.readTo(self.CR)
        head = self.getHead(res)
        while head not in ["OK", "FAIL"]:
            res = self.readTo(self.CR)
            head = self.getHead(res)
        return cmd, res


class ERXUDP:

    @staticmethod
    def tryparse(line):
        try:
            if line.startswith("ERXUDP"):
                erxudp = ERXUDP.parse(line)
                if erxudp is None:
                    return False, None
                return True, erxudp
            return False, None
        except ValueError:
            return False, None

    @classmethod
    # SA2レジスタが０の場合のみ動作
    def parse(erxudp, line):
        items = line.split(" ", 9)
        erxudp.header = items[0]
        erxudp.sender = items[1]
        erxudp.dest = items[2]
        erxudp.rport = items[3]
        erxudp.lport = items[4]
        erxudp.senderlla = items[5]
        erxudp.secured = items[6]
        erxudp.side = items[7]
        erxudp.datalen = items[8]
        erxudp.data = " ".join(items[9:])
        erxudp.id = " ".join([erxudp.sender, erxudp.dest,
                              erxudp.rport, erxudp.lport])
        return erxudp


class EVENT:
    @classmethod
    def parse(event, line):
        items = line.split(" ")
        event.header = items[0]
        event.num = items[1]
        event.sender = items[2]
        event.side = items[3]
        if len(items) > 4:
            event.param = items[4:]
        return event

    @staticmethod
    def tryparse(line):
        try:
            if line.startswith("EVENT"):
                event = EVENT.parse(line)
                if event is None:
                    return False, None
                return True, event
            return False, None
        except ValueError:
            return False, None


class bp35c0:
    handle = 4
    port = 10000
    portX = "%04X" % port
    side = 0

    def __init__(self, ser):
        self.cmd = commands(ser)
        self.Initialize()

    def Initialize(self):
        self.RESET()
        self.cmd.SKINFO()
        res = self.cmd.SKUDPPORT("%X" % bp35c0.handle, "%04X" % bp35c0.port)

    def SetCh(self, ch):
        res = self.cmd.SKSREG("S02", ch)

    def SetPANID(self, id):
        res = self.cmd.SKSREG("S03", id)

    def SetPWD(self, pw):
        res = self.cmd.SKSETPWD(pw)

    def SetRBID(self, id):
        res = self.cmd.SKSETRBID(id)

    def RESET(self):
        res = self.cmd.SKRESET()

    def EDScan(self, mask="FFFFFFFF"):
        res = self.cmd.SKSCAN("0", mask, "4", "0")

    def ACTIVEScan(self, mask="FFFFFFFF", timeout=25):
        cmd, res = self.cmd.SKSCAN("2", mask, "6", "0")
        paalist = []
        starttime = time.time()
        interval = 0
        while interval < timeout:
            res = self.readline(timeout=1)
            if res.startswith("EPANDESC"):
                paalist = self.getEPANDESC()
                return paalist
            elif res.startswith("EVENT 22"):
                print "active scan is timeout"
                return None
            interval = time.time() - starttime
        return None

    def getEPANDESC(self, paalist=None):
        if paalist is None:
            paalist = []
        hoge = {"head": "EPANDESC"}
        while True:
            res = self.readline()

            if res.startswith("EPANDESC"):
                # 再帰
                paalist.append(hoge)
                self.getEPANDESC(paalist)
            elif res.startswith("EVENT 22"):
                paalist.append(hoge)
                return paalist

            items = res.split(":")
            name = items[0].strip()
            param = items[1].strip()
            hoge[name] = param

    def Start(self):
        res = self.cmd.SKSTART()

    def Join(self, ipv6):
        res = self.cmd.SKJOIN(ipv6)
        return res

    def SKLL64(self, mac):
        res = self.cmd.SKLL64(mac)
        return res[1]

    def StartPAA(self, rbid, pwd, ch, panid):
        self.SetRBID(rbid)
        self.SetPWD(pwd)
        self.SetCh(ch)
        self.SetPANID(panid)
        self.Start()

    def JoinTo(self, rbid, pwd, ch, panid, ipv6, timeout=30):
        self.SetRBID(rbid)
        self.SetPWD(pwd)
        self.SetCh(ch)
        self.SetPANID(panid)
        self.Join(ipv6)
        st = time.time()
        # self.cmd.settimeout(1)
        while time.time() - st < timeout:
            line = self.cmd.readline()
            if len(line) == 0:
                continue
            if line.startswith("EVENT 24"):
                return False
            if line.startswith("EVENT 25"):
                return True
        return False

    def setTimeout(self, timeout=None):
        self.cmd.ser.timeout = timeout

    def readline(self, timeout=None):
        res = self.cmd.readline(timeout).rstrip()
        return res

    def sendto(self, rhost, rport_str, data):
        handleX = "%X" % bp35c0.handle
        res = self.cmd.SKSENDTO(handleX, rhost, rport_str, "2", "0", data)
        return res


class bp35c0_dummy:
    dummydata = "this is a dummy data!"

    def setdummydata(self, dummy):
        self.dummydata = dummy

    def readline(self, timeout=None):
        header = "ERXUDP"
        sender = 'FE80:0000:0000:0000:021D:1291:0000:12A0'
        dest = 'FE80:0000:0000:0000:021D:1291:0000:1A15'
        rport = '01EA'
        lport = '01EA'
        senderlla = '001D1291000012A0'
        secured = '2'
        side = '0'
        datalen = '%04X' % len(self.dummydata)
        data = self.dummydata
        return ' '.join([header, sender, dest, rport, lport, senderlla,
                         secured, side, datalen, data])

    def sendto(self, rhost, rport_str, data):
        print 'dummy:%s' % data
        return True, "OK"

    def Join(self, ipv6):
        return True, "OK"

    def StartPAA(self, rbid, pwd, ch, panid):
        return True, "OK"

    def JoinTo(self, rbid, pwd, ch, panid, ipv6, timeout=30):
        return True

    def Initialize(self):
        pass
