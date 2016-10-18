# -*- coding: gbk -*-
from ftplib import FTP
import re
import os
import telnetlib
import threading                # 线程
from multiprocessing.dummy import Pool  # 线程


class Update:
    def __init__(self):
        self.ips = []

    # 获取ip地址以及文件名称
    def getip(self, i):
        path = os.path.join(os.path.expanduser("~"), 'Desktop//')
        cwdsend = 'ramdisk'
        # 读取配置文件，获取ip地址及终端版本
        with open('mt_info.ini', 'r') as f:
            info = f.readlines()
            ip = re.findall('([\d\.]+)\t.*?', info[i])[0]
            sendfilename = re.findall('\t([\w\.\_]+)', info[i])[0]
        return ip, cwdsend, sendfilename, path

    # 获取文件名
    def getfilename(self, ip, cwd):
        try:
            ftp = FTP()
            timeout = 30
            port = 21
            ftp.connect(ip, port, timeout)
            ftp.login('admin', 'admin')

            print(ftp.getwelcome())
            ftp.cwd(cwd)
            print('上传完成后ramdisk中的文件')
            list = ftp.nlst()
            for name in list:
                print(name)
        except:
            print('%s无法显示文件目录，请检查ip地址是否正确！' % ip)

    # ftp登陆终端
    def ftp_mt(self, ip, cwd):
        ftp = FTP()
        timeout = 5
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

    # ftp下载文件，从服务器下载文件
    def getfile(self,ip, cwd, filename, path):
        try:
            ftp = self.ftp_mt(ip, cwd)
            ftp.retrbinary('RETR '+filename, open(path + filename,'wb').write)
            ftp.quit()
        except:
            print('%s下载文件失败...' % ip)

    # 上传文件
    def sendfile(self, ip, cwd, sendfilename, path):
        flag = 1
        try:
            ftp = self.ftp_mt(ip, cwd)
            print('%s开始上传 ...' % ip)
            ftp.storbinary('STOR ' + sendfilename, open(path+sendfilename, 'rb'))
            print('%s 升级文件上传成功，正在升级...' % ip)
            ftp.quit()
        except:
            print('%s连接超时...' % ip)
            self.ips.append(ip)
            flag = 0
        return flag

    #  调用上传文件、升级函数
    def mainfunc(self, ip, cwdsend, sendfilename, path):

        flag = self.sendfile(ip, cwdsend, sendfilename, path)
        if flag == 1:
            self.getfilename(ip, cwdsend)
            self.allupdate(ip, sendfilename)
        if threading.active_count() == 2:
            self.show_failed()

    # 多线程实现，不使用动态变量
    def the_start(self):
        threads = []
        print('Welcome!!!')
        print('请将升级包全部放置于桌面，并添加好配置文件，以table键作为配置文件间隔！！')
        with open('mt_info.ini', 'r') as f:
            info = f.readlines()
        mtn = len(info)
        for i in range(0, mtn):
            ip, cwdsend, sendfilename, path = self.getip(i)
            t = threading.Thread(target=self.mainfunc, args=(ip, cwdsend, sendfilename, path))
            threads.append(t)

        for th in threads:
            th.start()
        th.join()

    # 通过multiprocessing.dummy暂时无法实现，无法实现传递多个参数，只能确定一个升级版本，实现多终端升级
    def pool_start(self):
        args = []
        print('Welcome!!!')
        mtn = int(input('请输入想要升级的终端个数：'))
        for i in range(0, mtn):
            ip, cwdsend, sendfilename, path = self.getip(i+1)
            t = (ip, cwdsend, sendfilename, path)
            print(type(t))
            args.append(t)
        pool = Pool(8)
        pool.map(self.mainfunc, args)

    # 执行上传的文件，进行升级
    def allupdate(self, ip, sendfilename):
        commands = ['she', 'cd ramdisk', 'allupdate %s' % sendfilename, 'reboot']
        try:
            tn = self.telnet_mt(ip, 23, 150)
            print('%s正在升级请稍后...'% ip)
            # 检测到Router#就输入命令
            tn.read_until('#'.encode())
            for command in commands:
                tn.write(command.encode('ascii')+b'\r\n')
            tn.read_all()
            # 关闭连接
            tn.close()
        except:
            print('%s telnet连接断开，升级成功...' % ip)
            self.get_ver(ip, 2500)

    # telnet连接终端
    def telnet_mt(self, ip, port, timeout):
        username = 'admin'
        password = 'admin'
        tn = telnetlib.Telnet(ip, port, timeout)
        tn.set_debuglevel(5)
        tn.read_until('Username:'.encode())
        # 输入用户名
        tn.write(username.encode('ascii') + b'\r\n')
        tn.read_until('Password:'.encode())
        # 输入密码
        tn.write(password.encode('ascii') + b'\r\n')
        return tn

    # 获取终端版本信息
    def get_ver(self, ip, port):
        try:
            tn = self.telnet_mt(ip, port, 10)
            tn.read_until('>'.encode())
            tn.write('mtver'.encode() + b'\r\n')
            tn.read_until('>'.encode())
            tn.close()
            print('%s 获取版本信息成功！' % ip)
        except:
            print('%s获取版本信息成功失败' % ip)

    # 显示未连接成功终端
    def show_failed(self):
        count = 0
        print('所有终端升级完成')
        print('未连接成功终端如下：')
        for j in self.ips:
            print(j)
            count += 1
        print('共%d台' % count)

if __name__ == '__main__':
    start = Update()
    start.the_start()








