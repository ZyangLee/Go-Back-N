import udt
import socket
from ctypes import c_ushort

MAX_SEQ = 8
WINDOW_SIZE = 5


def CRCCCITT(info):
    loc = [16, 12, 5, 0]
    p = [0 for i in range(17)]
    for i in loc:
        p[16-i] = 1
    # print(p)
    info_list = []
    for single_info in info:
        # print('sigle_info:', single_info)
        bin_s = bin(single_info).replace('0b', '')
        bin_s_len = len(bin_s)
        for i in range(8 - bin_s_len):
            info_list.append(0)
        for j in bin_s:
            info_list.append(int(j))
    info = info_list.copy()
    # print(info)
    times = len(info)

    for i in range(16):
        info.append(0)

    for i in range(times):
        if info[i] == 1:
            for j in range(17):
                info[j + i] = info[j+i] ^ p[j]

    # print(info)
    check_code = info[-16::]
    check_sum = 0
    for i in range(16):
        check_sum = check_sum * 2 + check_code[i]
    return check_sum


def CRCCCITT_valid(info):
    loc = [16, 12, 5, 0]
    p = [0 for i in range(17)]
    for i in loc:
        p[16-i] = 1
    info_list = []
    for single_info in info:
        # print('sigle_info:', single_info)
        bin_s = bin(single_info).replace('0b', '')
        bin_s_len = len(bin_s)
        for i in range(8 - bin_s_len):
            info_list.append(0)
        for j in bin_s:
            info_list.append(int(j))
    info = info_list.copy()
    times = len(info) - 16
    # print(info)
    for i in range(times):
        if info[i] == 1:
            for j in range(17):
                info[j + i] = info[j+i] ^ p[j]

    check_code = info[-16::]
    check_sum = 0
    for i in range(16):
        check_sum = check_sum * 2 + check_code[i]
    return check_sum


def between(a, b, c):
    if (a <= b < c) or (c < a <= b) or (b < c < a):
        return True
    else:
        return False


def make(frame_nr, frame_expected, data_value, data=b''):  # frame编号，作为接收方期望接收的frame、源文件
    ack = (frame_expected + MAX_SEQ - 1) % MAX_SEQ
    ack_bytes = ack.to_bytes(1, byteorder='big', signed=False)
    seq = frame_nr % MAX_SEQ
    seq_bytes = seq.to_bytes(1, byteorder='big', signed=False)
    data_value_bytes = data_value.to_bytes(1, byteorder='big', signed=False)
    # prefix = ('%3d%3d%1d' % (seq, ack, data_value))
    prefix = seq_bytes + ack_bytes + data_value_bytes
    checksum = CRCCCITT(prefix+data)
    checksum = checksum.to_bytes(2, byteorder='big', signed=False)
    return prefix + data + checksum


def make_sentinel():
    return b''


def extract(packet):
    seq = packet[0]
    ack = packet[1]
    data_value = packet[2]
    data = packet[3:-2]
    checksum = int.from_bytes(packet[-2:], byteorder='big', signed=False)
    return seq, ack, data_value, data, checksum


if __name__ == '__main__':
    frame = make(0, 1, 1, b'')
    # print(frame)
    # print(extract(frame))
    # print(CRCCCITT_valid(frame))
    # test = 0xa
    # tst = bin(test)
    # print(tst, type(tst))
    # CRCCCITT(b'\xaa\xff\xff')



