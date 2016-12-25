#!/usr/bin/python

#  Copyright (C) 2015, Samsung Electronics, Co., Ltd. All Rights Reserved.
#  #  Written by System S/W 2 Group, S/W Platform R&D Team,
#  #  Mobile Communication Division.
#  ##
#
#  ##
#  # Project Name : pyodin
#  #
#  # Project Description :
#  #
#  # Comments : tabstop = 8, shiftwidth = 8 noexpandtab
#  ##
#
#  ##
#  # File Name : pyodin.py
#  #
#  # File Description :
#  #
#  # Author : Byeong Jun Mun(bjun.mun@samsung.com)
#  # Dept : System S/W R&D Team Grp.2
#  # Created Date : 09-June-2015
#  # Last Update: 1-Sep-2015
#  ##

VERSION = "0.952"

import os
import sys
import getopt
import tarfile
import serial
import struct
import array
import time, threading
import commands
import signal
import wx
from select import select

CHECKSUM_FILE_END = 0x0A
CHECKSUM_FILE_START = 0x20
CHECKSUM_FILE_COUNT = 64
CHECKSUM_FILE_NUM_VALID = 3
MD5_CHECKSUM_SIZE_ASCII = 32
MD5_SIZE = 512

CMD_INIT = 100
CMD_PIT = 101
CMD_XMIT = 102
CMD_CLOSE = 103

CMD_INIT_TARGET = 0
CMD_INIT_RESET_TIME = 1
CMD_INIT_TOTAL_SIZE = 2

CMD_PIT_SET = 0
CMD_PIT_GET = 1
CMD_PIT_START = 2
CMD_PIT_COMPLETE = 3

CMD_XMIT_DOWNLOAD = 0
CMD_XMIT_DUMP = 1
CMD_XMIT_START = 2
CMD_XMIT_COMPLETE = 3

CMD_CLOSE_END = 0
CMD_CLOSE_REBOOT = 1

PKT_DATA_SIZE = 131072 # 128KB
PKT_DUMP_SIZE = 500

DEVICE_TYPE_ONENAND = 0
DEVICE_TYPE_NAND = 1
DEVICE_TYPE_MOVINAND = 2

PARTITION_ATTR_RO = 0
PARTITION_ATTR_RW = 1
PARTITION_ATTR_STL = 2


bin_file_names = []
bin_files = []

def XMIT_DATA_START_SIZE(x):
    return ((((x - 1) >> 17) + 1) << 17)

class PyodinThread(threading.Thread):

    def __init__(self, dev_path, file_pathes):
        threading.Thread.__init__(self)
        self.__suspend = False
        self.__exit = False
        self.serial_dev_str = dev_path
        self.serial_dev = serial.Serial(dev_path)
        self.file_size_dl = 0

        self.partition_bin_type = []
        self.partition_device_type = []
        self.partition_id = []
        self.partition_type = []
        self.partition_filesystem_type = []
        self.partition_block_size = []
        self.partition_block_len = []
        self.partition_offset = []
        self.partition_filesize = []
        self.partition_name = []
        self.partition_file_name = []
        self.partition_delta_name = []

        self.bin_file_names = []
        self.bin_files = []
        self.m_total_size = 0


        self.file_pathes = file_pathes

        self.pit_file = None

        for file_path in self.file_pathes:
            if file_path.find(".pit") >= 0:
                self.pit_file = file_path
                self.file_pathes.remove(file_path)

        self.progress = None
        self.statusText = None

    def setProgressBar(self, progress):
        self.progress = progress

    def setStatusText(self, text):
        self.statusText = text

    def file_analysis(self, file_pathes):
        self.m_total_size = 0
        print "========================================"
        for file_path in self.file_pathes:
            t = tarfile.open(file_path, 'r')
            for filename in t.getnames():
                try:
                    f = t.extractfile(filename)
                except KeyError:
                    print 'ERROR: Did not find %s in tar archive' % filename
                    return None
                else:
                    print "%-28s(%d)" % (filename, f.size)
                    self.bin_files.append(f)
                    self.bin_file_names.append(filename)
                    self.m_total_size += f.size

        print "========================================"

        return True

    def run(self):
        ret = self.file_analysis(self.file_pathes)
        if ret is None:
            return

        ret = self.setup_connection()
        if ret is None:
            print "Cannot connect to device : " + self.serial_dev_str
            return None

        ret = self.initialization()
        if ret is None:
            return None


        ret = self.set_pit(self.pit_file)
        if ret is None:
            return None

        ret = self.get_pit_from_device()
        if ret is None:
            return None

        ret = self.pda_download()
        if ret is None:
            return None

        self.end_connection()
        if self.progress is not None:
            wx.CallAfter(self.progress.SetValue, 0)

        return True

    def setup_connection(self):
        try:
            self.serial_dev.write("ODIN")
            ack = self.serial_dev.read(4)
            print "[" + self.serial_dev_str + "] Loke : " + ack
        except serial.serialutil.SerialException, e:
            self.serial_dev.close()
            print e
            return None
        return True


    def initialization(self):
        print "[" + self.serial_dev_str + "] Try to request the device informations"
        ret = self.request2a(CMD_INIT, CMD_INIT_TARGET)
        if ret is None:
            return ret

        print "[" + self.serial_dev_str + "] Platform %d, Revisiton %d" % ((ret & 0xff00) >> 8, (ret &0x00ff))
        ret = self.request2a(CMD_INIT, CMD_INIT_RESET_TIME)
        if ret is None:
            print "Error: request CMD_INIT_RESET_TIME"
            return ret

        tx_ndata = [0] * 9
        tx_ndata[0] = self.m_total_size
        ret = self.request4a(CMD_INIT, CMD_INIT_TOTAL_SIZE, tx_ndata, 1);
        if ret is None:
            print "Error: request CMD_INIT_TOTAL_SIZE"
            return ret

        return True

    def set_pit(self, pit_file):
        if pit_file is None:
            return True

        fd = open(pit_file, 'rb')
        pit_size = os.fstat(fd.fileno()).st_size

        buf = bytes()
        buf = fd.read(pit_size)
        print "[" + self.serial_dev_str + "] Start Repartition"
        self.pit_analysis(buf)

        try:
            self.request2a(CMD_PIT, CMD_PIT_SET);
            tx_ndata = [0] * 9
            tx_ndata[0] = pit_size
            self.request4a(CMD_PIT, CMD_PIT_START, tx_ndata, 1);
            self._xmit_data(buf);
            self.request4a(CMD_PIT, CMD_PIT_COMPLETE, tx_ndata, 1);
        except serial.serialutil.SerialException, e:
            self.serial_dev.close()
            fd.close()
            print e
            return None

        fd.close()
        return True

    def get_pit_from_device(self):
        print "[" + self.serial_dev_str + "] Get PIT from the target"

        size = self.request2a(CMD_PIT, CMD_PIT_GET)
        if size < 0:
            print "[" + self.serial_dev_str + "] Error! Get PIT"
            return

        pit_packet = bytes()
        count = ((size - 1) / PKT_DUMP_SIZE + 1)

        data_arr = [0] * 9

        try:
            for i in xrange(0, count):
                data_arr[0] = i
                self.request4x(CMD_PIT, CMD_PIT_START, data_arr, 1);
                pit_packet += self.serial_dev.read(min(PKT_DUMP_SIZE, size - (PKT_DUMP_SIZE * i)))

        except serial.serialutil.SerialException, e:
            self.serial_dev.close()
            print e
            return None

#       print pit_packet
        ret = self.request2a(CMD_PIT, CMD_PIT_COMPLETE)
        if ret is None:
            return ret

        self.pit_analysis(pit_packet)
        return True

    def pit_analysis(self, pit_packet):

        pit_header_magic = struct.unpack('I', pit_packet[:4])[0]
        pit_header_count = struct.unpack('i', pit_packet[4:8])[0]
        pit_header_dummy = struct.unpack('5i', pit_packet[8:28])

        print "[" + self.serial_dev_str + "] pit magic : 0x%x count : %d" % (pit_header_magic, pit_header_count)
        for i in xrange(0, pit_header_count):
            pit_data = pit_packet[28 + i * 132: 28 + (i + 1) * 132]
            partition_info_pack = struct.unpack('iiiiiiiii32s32s32s', pit_data)
            self.partition_bin_type.append(partition_info_pack[0])
            self.partition_device_type.append(partition_info_pack[1])
            self.partition_id.append(partition_info_pack[2])
            self.partition_type.append(partition_info_pack[3])
            self.partition_filesystem_type.append(partition_info_pack[4])
            self.partition_block_size.append(partition_info_pack[5])
            self.partition_block_len.append(partition_info_pack[6])
            self.partition_offset.append(partition_info_pack[7])
            self.partition_filesize.append(partition_info_pack[8])
            self.partition_name.append(partition_info_pack[9])
            self.partition_file_name.append(partition_info_pack[10])
            self.partition_delta_name.append(partition_info_pack[11])

#            print "%s %d" %  (partition_info_pack[9], partition_info_pack[1])


    def get_xmit_size(self, pt_index):

        device_type = self.partition_device_type[pt_index]

        if device_type is DEVICE_TYPE_NAND or \
                device_type is DEVICE_TYPE_MOVINAND:
            return (128 * 1024 * 240)
#        elif device_type is DEVICE_TYPE_ONENAND:
        else:
            block_size = self.partition_device_block_size[pt_index]

            f = block_size / 128
            s = 4 * f
            c = 800 / f

            size = block_size

            if self.partition_type[pt_index] is PARTITION_ATTR_RW:
                size += s

            return (size * 1024 * c)


    def pda_download(self):
        bin_cnt = 0
        data_arr = [0] * 9
        ndata = [0] * 9

        for binary in self.bin_files:
            pos = binary.size
            cnt = 0
            for name in self.partition_file_name:

                if name.find(self.bin_file_names[bin_cnt]) >= 0 \
                    or (name.find(".pit") >= 0 and self.bin_file_names[bin_cnt].find(".pit") >= 0):
                    bin_type = self.partition_bin_type[cnt]
                    device_type = self.partition_device_type[cnt]
                    parti_id = self.partition_id[cnt]
                    block_size = self.partition_block_size[cnt]
                    break

                cnt += 1

            if cnt < len(self.partition_name):
                print "[" + self.serial_dev_str + "] Download [%s] %s Bytes: %s" % \
                        (self.partition_name[cnt], self.bin_file_names[bin_cnt], binary.size)
            else:
                print "[" + self.serial_dev_str + "] Download [] %s Bytes: %s" % \
                        (self.bin_file_names[bin_cnt], binary.size)

            if self.statusText is not None:
                wx.CallAfter(self.statusText.SetValue, self.bin_file_names[bin_cnt])
#                self.statusText.SetValue(self.bin_file_names[bin_cnt])

            if cnt < len(self.partition_file_name):
                pack_size = self.get_xmit_size(cnt)

#            self.file_size_dl = 0
            while pos > 0:
                down_len = min(pos, pack_size)
                ret = self.request2a(CMD_XMIT, CMD_XMIT_DOWNLOAD);
                if ret is None:
                    return None

                data_arr[0] = XMIT_DATA_START_SIZE(down_len)
                ret = self.request4a(CMD_XMIT, CMD_XMIT_START, data_arr, 1)
                if ret is None:
                    return None

                self.xmit_data(binary, down_len)

                pos -= down_len
                ndata[0] = 0    #pda
                ndata[1] = down_len
                ndata[2] = bin_type
                ndata[3] = device_type
                ndata[4] = parti_id
                if pos is 0:
                    ndata[5] = 1
                else:
                    ndata[5] = 0
                ndata[6] = 0
                ndata[7] = 0

                ret = self.request4a(CMD_XMIT, CMD_XMIT_COMPLETE, ndata, 8)
                if ret is None:
                    return None

            bin_cnt += 1
        return True

    def end_connection(self):
        self.request2a(CMD_CLOSE, CMD_CLOSE_END)
        time.sleep(1)
        print "[" + self.serial_dev_str + "] Rebooting"
        self.request2a(CMD_CLOSE, CMD_CLOSE_REBOOT)

        if self.progress is not None:
#            self.progress.SetValue(0)
            wx.CallAfter(self.progress.SetValue, 0)

    def _xmit_data(self, buf):
        try:
            self.serial_dev.write(buf)
            ack = self.serial_dev.read(8)
            rx_id = struct.unpack('i', ack[:4])[0]
            rx_ack = struct.unpack('i', ack[4:8])[0]
            return True
        except serial.serialutil.SerialException, e:
            self.serial_dev.close()
            print e
            return None

    def xmit_data(self, binary, size):
        pos = 0
        while pos < size:
            down_len = min(size - pos, PKT_DATA_SIZE)
            buf = binary.read(down_len)

            if down_len < PKT_DATA_SIZE:
                dummy_size = PKT_DATA_SIZE - down_len
                dummy_buf = [0] * dummy_size
                dummy_buf_arr = array.array('B', dummy_buf)
                buf += struct.pack('%dB' % dummy_size, *dummy_buf_arr)

            if self._xmit_data(buf) is None:
                return None

            pos += down_len

            self.file_size_dl += down_len
            if self.progress is not None:
                wx.CallAfter(self.progress.SetValue, self.file_size_dl * 100. / self.m_total_size)
#                self.progress.SetValue(self.file_size_dl * 100. / self.m_total_size)
#            status = r"%10d  [%3.2f%%]" % (self.file_size_dl, self.file_size_dl * 100. / binary.size)
#            status = status + chr(8)*(len(status)+1)
#            print status,
        return True

    def request2a(self, id, dataid):
        tx_ndata = [0]*9
        tx_sdata = [0]*128
        tx_md5 = [0]*32

        return self.request(id, dataid, tx_ndata, 0, tx_sdata, tx_md5, True)

    def request4a(self, id, dataid, d, c):
        tx_ndata = d
        tx_sdata = [0]*128
        tx_md5 = [0]*32
        return self.request(id, dataid, tx_ndata, c, tx_sdata, tx_md5, True)

    def request4x(self, id, dataid, d, c):
        tx_ndata = d
        tx_sdata = [0]*128
        tx_md5 = [0]*32
        return self.request(id, dataid, tx_ndata, c, tx_sdata, tx_md5, False)

    def request(self, id, dataid, pdata, count, msg, md5, ack):
        tx_id = id
        tx_dataid = dataid

        tx_ndata = pdata
        tx_sdata = msg
        tx_md5 = md5
        tx_dummy = [0]*820

        packet = self.packTxPacket(tx_id, tx_dataid, tx_ndata, tx_sdata, tx_md5, tx_dummy)
        try:
            self.serial_dev.write(packet)
        except serial.serialutil.SerialException, e:
            print e
            self.serial_dev.close()
            return None

        if ack is True:
            return self.waitForAck(tx_id)

        return True

    def waitForAck(self, tx_id):
        try:
            ack = self.serial_dev.read(8)
            rx_id = struct.unpack('i', ack[:4])[0]
            rx_ack = struct.unpack('i', ack[4:8])[0]

            if rx_id == 0xffffffff or rx_id is not tx_id:
                print "[" + self.serial_dev_str + "] Error! Request id %d failed. error code = %x" % (tx_id, rx_id)
                return None

        except serial.serialutil.SerialException, e:
            self.serial_dev.close()
            print e
            return None

        return rx_ack

    def packTxPacket(self, id, dataid, nData, sData, md5, dummy):
        packet = bytes()
        nDataArray = array.array('i', nData)
        sDataArray = array.array('B', sData)
        md5Array = array.array('B', md5)
        dummyArray = array.array('B', dummy)

        packet = struct.pack('11i', id, dataid, *nData)
        packet += struct.pack('128B', *sDataArray)
        packet += struct.pack('32B', *md5Array)
        packet += struct.pack('820B', *dummyArray)
        return packet

    def unpackRxPacket(self, packet):
        rx_id = struct.unpack('i', packet[:4])
        rx_dataid = struct.unpack('i', packet[4:8])

        print "[" + self.serial_dev_str + "] rx id : %d data id : %d" % (rx_id, rx_dataid)
        return rx_id, rx_dataid

def get_devices():
    status, output = commands.getstatusoutput("ls /dev/ttyACM*")
    dev_pathes = output.split("\n")

    if output.find('cannot access') > 0:
        return None

    return dev_pathes


def getch():
    return sys.stdin.read(4)

def kbhit():
    dr,dw,de = select([sys.stdin], [], [], 0)
    return dr <> []

def kbfunc():
    if kbhit():
        ret = getch()
    else:
        ret = False

    return ret

def cmdQuit():
    kb = kbfunc()

    if kb != False and kb == 'quit':
        print "Quit PYODIN"
        return True

    return False

def quit(event):
    print "you pressed control-forwardslash"
    work_continue = False

def signal_handler(signal, frame):
    print('Quit after downloading')
    sys.exit(0)

work_continue = False

if __name__ == '__main__':
    file_pathes = []

#    updater_path = os.path.dirname(os.path.abspath( __file__ )) + '/updater.sh'
#    isUpdate = os.system(updater_path)
#    if isUpdate != 0:
#        os.execv(__file__, sys.argv)
#        sys.exit(0)

    for file_path in sys.argv[1:]:
#        if file_path.find(".pit") >= 0:
#            pit_file = file_path
        if file_path == '-c':
            work_continue = True
        else:
            file_pathes.append(file_path)

    signal.signal(signal.SIGINT, signal_handler)

    print "PYODIN Version : " + VERSION
    current_devices = []
    devices = get_devices()
    if devices is None:
        print "Wating for the new device."

    while(cmdQuit() is False):

        devices = get_devices()
        if devices is None:
            if len(current_devices) > 0:
                print "Detached " + current_devices[0]
                print "Waiting for the new device."
                del current_devices[:]

            time.sleep(0.5)
            continue

        time.sleep(0.5)

        for dev in devices:
            cnt = 0
            for current_dev in current_devices:
                if dev.find(current_dev) >= 0:
                    break
                cnt += 1

            if cnt is len(current_devices):
                print "Attached " + dev
                current_devices.append(dev)
                t = PyodinThread(dev, file_pathes)
                t.start()

        if len(current_devices) > 0:
            cur_cnt = 0
            for cur_dev in current_devices:
                cnt = 0
                for dev in devices:
                    if dev.find(cur_dev) >= 0:
                        break
                    cnt += 1

                if cnt is len(devices):
                    print "Detached " + cur_dev
                    del current_devices[cur_cnt]
                cur_cnt += 1

        if work_continue is False:
            break

