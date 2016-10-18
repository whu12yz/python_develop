import MT_update
import telnetlib
import os
from ftplib import FTP
import re
import threading


class Movefile():
    def change(self, ip, sendfilename):
        commands = ['she', 'cd ramdisk', 'chmod 777 %s' % sendfilename, 'mv %s /usr/bin' % sendfilename, 'ls', 'reboot' ]
        try:
            tn = MT_update.telnet_mt(ip, 23, 10)
            if tn.read_until('#'.encode()) or tn.read_until('$'.encode()):     # 检测到Router#就输入命令,兼容终端和板卡
                for command in commands:
                    tn.write(command.encode('ascii') + b'\r\n')
                info = tn.read_all()
                print(info)
                # 关闭连接
                tn.close()
            else:
                print('文件覆盖失败！')
        except:
            print('%s 文件覆盖成功' % ip)
            # MT_update.get_ver(ip)

    def ftp_mt(self, ip, cwd):
        ftp = FTP()
        timeout = 30
        port = 21
        ftp.connect(ip, port, timeout)
        ftp.login('admin', 'admin')

        print(ftp.getwelcome())
        ftp.cwd(cwd)
        print('%s ramdisk中已有文件如下:' % ip)
        list = ftp.nlst()
        for name in list:
            print(name)
        return ftp

    def sendfile(self, ip,cwd, sendfilename, path):              # 上传文件
        flag = 1
        try:
            ftp = self.ftp_mt(ip, cwd)

            print('%s开始上传 ...' % ip)
            ftp.storbinary('STOR '+sendfilename, open(path+sendfilename, 'rb'))
            print('%s 文件上传成功' % ip)
            ftp.quit()
        except:
            print('%s连接超时...' % ip)
            flag = 0
        return flag

    # 获取ip地址以及文件名称
    def getip(self, i):
        path = os.path.join(os.path.expanduser("~"), 'Desktop//')
        cwdsend = 'ramdisk'
        # 读取配置文件，获取ip地址及终端版本
        with open('mcu.ini', 'r') as f:
            info = f.readlines()
            ip = re.findall('(.*?)\t.*?', info[i])[0]
            sendfilename = re.findall('\t(\w+.\w+)', info[i])[0]
        return ip, cwdsend, sendfilename, path

    # 多线程实现，不使用动态变量
    def the_start(self):
        threads = []
        print('Welcome!!!')
        with open('mcu.ini', 'r') as f:
            info = f.readlines()
        mtn = len(info)
        for i in range(0, mtn):
            ip, cwdsend, sendfilename, path = self.getip(i)
            t = threading.Thread(target=self.change_mainfunc, args=(ip, cwdsend, sendfilename, path))
            threads.append(t)
        for t in threads:
            t.start()
        t.join()

    #  调用上传文件、升级函数
    def change_mainfunc(self, ip, cwdsend, sendfilename, path):
        flag = self.sendfile(ip, cwdsend, sendfilename, path)
        if flag == 1:
            MT_update.getfilename(ip, cwdsend)
            self.change(ip, sendfilename,)


if __name__ == '__main__':
    begin = Movefile()
    begin.the_start()