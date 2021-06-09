import packet
import socket
from timer import Timer
import time
import threading
import udt


MAX_SEQ = 8
WINDOW_SIZE = 5


def set_window_size(num_packets, base):
    return min(5, num_packets - base)


def inc(num):
    return (num+1) % MAX_SEQ


# Sets the window size
class CLIENT:
    MY_ADDR = ('localhost', 43056)
    YOUR_ADDR = ('localhost', 43057)
    frame_expected = 0  # 0 ~ MAX_SEQ-1
    send_timer = Timer(0.5)
    base = 0  # 0 ~ num_packets
    is_sending = 0
    next_frame_to_send = 0  # 0 ~ num_packets
    ack_expected = 0  # 0 ~ MAX_SEQ-1
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(MY_ADDR)
    sock.settimeout(3)  # 设定时间上限3s

    def sender(self, filename):
        self.is_sending = 1  # 正在发送
        # 绑定端口
        # 将要发送的文件拆分，存储到packets中
        packets = []
        try:
            file = open(filename, 'rb')
        except IOError:
            print('Unable to open', filename)
            return

        while True:
            data = file.read(1024)
            if not data:
                break
            packets.append(data)

        num_packets = len(packets)
        print('I got ' + str(num_packets) + ' packets')
        window_size = set_window_size(num_packets, self.base)

        # 循环发送数据包，直到数据包全部发出
        while self.base < num_packets:
            # 为数据包添加前缀和校验位构成frame
            while self.next_frame_to_send < self.base + window_size:
                s = packet.make(self.next_frame_to_send, self.frame_expected, 1, packets[self.next_frame_to_send])
                # 发送数据包
                udt.send(s, self.sock, self.YOUR_ADDR)
                self.next_frame_to_send += 1
                window_size = set_window_size(num_packets, self.base)  # 防止packets越界
            # 将窗口内所有数据包发出后，打开计时器
            if not self.send_timer.running():
                # print('start timer')
                self.send_timer.start()

            # 等待计时器超时或收到ACK
            while self.send_timer.running() and not self.send_timer.timeout():
                # print('sleeping')
                time.sleep(0.5)

            # 计时器超时，需要重发
            if self.send_timer.timeout():
                print('超时，需要重发')
                self.send_timer.stop()
                self.next_frame_to_send = self.base
            else:  # 收到ACK
                print('在发送完窗口内所有数据后，收到ACK')
                window_size = set_window_size(num_packets, self.base)  # 防止packets越界
        self.is_sending = 0
        udt.send(packet.make_sentinel(), self.sock, self.YOUR_ADDR)  # 发送哨兵，表明发送结束或没有发送数据任务
        print('already sent')

    def receiver(self, filename):
        print('client1\'s receiver is running')
        # 将packet中信息保存到文件中
        try:
            file = open(filename, 'wb')
        except IOError:
            print('Unable to open', filename)
            return
        receive_all_data = False
        while True:
            if receive_all_data and self.is_sending == 0:  # 没有发送数据且不需要为发送进程接收ack，结束循环，不再接收数据
                break
            try:
                pkt, addr= udt.recv(self.sock)
            except socket.error:
                continue
            if not pkt:  # 所有数据包全部被接收
                file.close()  # 关闭文件
                receive_all_data = True
                print('already received all data!')
                continue  # 跳过下面解析包的操作
            seq, ack, data_value, data, check_sum = packet.extract(pkt)
            # print(f'接收包 序列号：{seq}, ack：{ack}, 是否有数据：{data_value}, 期望包号: {self.frame_expected}, '
            #       f'循环冗余校验码: {check_sum}')

            # 对收到包进行冗余校验，如果检查包有问题直接丢包
            if packet.CRCCCITT_valid(pkt) != 0:
                print('收到包有错误')
                continue

            # 当前类既作为发送者，又作为接收者
            # 1.为发送进程更新base 2.如果携带数据，需要接收数据并更新frame_expected
            if self.is_sending == 1:
                # 更新base到ack的后一位
                if packet.between(self.base % MAX_SEQ, ack, self.next_frame_to_send % MAX_SEQ):
                    while packet.between(self.base % MAX_SEQ, ack, self.next_frame_to_send % MAX_SEQ):
                        self.base += 1
                    # print('base updated', self.base)
                    self.send_timer.stop()  # 发送进程的计时器停止计时
                if data_value == 1:  # 对面发来的包有数据
                    if seq == self.frame_expected:
                        # 确认数据为当前希望接收的数据
                        self.frame_expected = inc(self.frame_expected)
                        file.write(data)
            # 当前类仅作为接收者，需要单独发送ACK
            else:
                if seq == self.frame_expected:
                    self.frame_expected = inc(self.frame_expected)
                    pkt_ack = packet.make(0, self.frame_expected, 0)  # data段为空
                    udt.send(pkt_ack, self.sock, self.YOUR_ADDR)
                    file.write(data)
                else:
                    pkt_ack = packet.make(0, self.frame_expected, 0)
                    udt.send(pkt_ack, self.sock, self.YOUR_ADDR)
        print('接收进程终止')


if __name__ == '__main__':
    client1 = CLIENT()
    client_receiver = threading.Thread(target=client1.receiver, args=('./copy2.txt',))
    client_receiver.start()
    client_sender = threading.Thread(target=client1.sender, args=('./test1.txt',))
    client_sender.start()
    client_receiver.join()
    client_sender.join()







