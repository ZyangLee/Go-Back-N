# 双工GBN（python实现）

运行方法：分别运行client1和client2，可以实现双工传输文件

### 各个文件功能

* packet.py：负责数据帧的制作
* timer.py：实现一个简单的定时器
* udt.py：模拟数据帧在物理层上传输可能出现的丢失或出错情况
* clinet.py：模拟用户
