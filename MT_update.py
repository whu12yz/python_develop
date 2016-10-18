# -*- coding: gbk -*-
from ftplib import FTP
import re
import os
import telnetlib
import threading                # �߳�
from multiprocessing.dummy import Pool  # �߳�


class Update:
    def __init__(self):
        self.ips = []

    # ��ȡip��ַ�Լ��ļ�����
    def getip(self, i):
        path = os.path.join(os.path.expanduser("~"), 'Desktop//')
        cwdsend = 'ramdisk'
        # ��ȡ�����ļ�����ȡip��ַ���ն˰汾
        with open('mt_info.ini', 'r') as f:
            info = f.readlines()
            ip = re.findall('([\d\.]+)\t.*?', info[i])[0]
            sendfilename = re.findall('\t([\w\.\_]+)', info[i])[0]
        return ip, cwdsend, sendfilename, path

    # ��ȡ�ļ���
    def getfilename(self, ip, cwd):
        try:
            ftp = FTP()
            timeout = 30
            port = 21
            ftp.connect(ip, port, timeout)
            ftp.login('admin', 'admin')

            print(ftp.getwelcome())
            ftp.cwd(cwd)
            print('�ϴ���ɺ�ramdisk�е��ļ�')
            list = ftp.nlst()
            for name in list:
                print(name)
        except:
            print('%s�޷���ʾ�ļ�Ŀ¼������ip��ַ�Ƿ���ȷ��' % ip)

    # ftp��½�ն�
    def ftp_mt(self, ip, cwd):
        ftp = FTP()
        timeout = 5
        port = 21
        ftp.connect(ip, port, timeout)
        ftp.login('admin', 'admin')

        print(ftp.getwelcome())
        ftp.cwd(cwd)
        print('%s ramdisk�������ļ�����:' % ip)
        list = ftp.nlst()
        for name in list:
            print(name)
        return ftp

    # ftp�����ļ����ӷ����������ļ�
    def getfile(self,ip, cwd, filename, path):
        try:
            ftp = self.ftp_mt(ip, cwd)
            ftp.retrbinary('RETR '+filename, open(path + filename,'wb').write)
            ftp.quit()
        except:
            print('%s�����ļ�ʧ��...' % ip)

    # �ϴ��ļ�
    def sendfile(self, ip, cwd, sendfilename, path):
        flag = 1
        try:
            ftp = self.ftp_mt(ip, cwd)
            print('%s��ʼ�ϴ� ...' % ip)
            ftp.storbinary('STOR ' + sendfilename, open(path+sendfilename, 'rb'))
            print('%s �����ļ��ϴ��ɹ�����������...' % ip)
            ftp.quit()
        except:
            print('%s���ӳ�ʱ...' % ip)
            self.ips.append(ip)
            flag = 0
        return flag

    #  �����ϴ��ļ�����������
    def mainfunc(self, ip, cwdsend, sendfilename, path):

        flag = self.sendfile(ip, cwdsend, sendfilename, path)
        if flag == 1:
            self.getfilename(ip, cwdsend)
            self.allupdate(ip, sendfilename)
        if threading.active_count() == 2:
            self.show_failed()

    # ���߳�ʵ�֣���ʹ�ö�̬����
    def the_start(self):
        threads = []
        print('Welcome!!!')
        print('�뽫������ȫ�����������棬����Ӻ������ļ�����table����Ϊ�����ļ��������')
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

    # ͨ��multiprocessing.dummy��ʱ�޷�ʵ�֣��޷�ʵ�ִ��ݶ��������ֻ��ȷ��һ�������汾��ʵ�ֶ��ն�����
    def pool_start(self):
        args = []
        print('Welcome!!!')
        mtn = int(input('��������Ҫ�������ն˸�����'))
        for i in range(0, mtn):
            ip, cwdsend, sendfilename, path = self.getip(i+1)
            t = (ip, cwdsend, sendfilename, path)
            print(type(t))
            args.append(t)
        pool = Pool(8)
        pool.map(self.mainfunc, args)

    # ִ���ϴ����ļ�����������
    def allupdate(self, ip, sendfilename):
        commands = ['she', 'cd ramdisk', 'allupdate %s' % sendfilename, 'reboot']
        try:
            tn = self.telnet_mt(ip, 23, 150)
            print('%s�����������Ժ�...'% ip)
            # ��⵽Router#����������
            tn.read_until('#'.encode())
            for command in commands:
                tn.write(command.encode('ascii')+b'\r\n')
            tn.read_all()
            # �ر�����
            tn.close()
        except:
            print('%s telnet���ӶϿ��������ɹ�...' % ip)
            self.get_ver(ip, 2500)

    # telnet�����ն�
    def telnet_mt(self, ip, port, timeout):
        username = 'admin'
        password = 'admin'
        tn = telnetlib.Telnet(ip, port, timeout)
        tn.set_debuglevel(5)
        tn.read_until('Username:'.encode())
        # �����û���
        tn.write(username.encode('ascii') + b'\r\n')
        tn.read_until('Password:'.encode())
        # ��������
        tn.write(password.encode('ascii') + b'\r\n')
        return tn

    # ��ȡ�ն˰汾��Ϣ
    def get_ver(self, ip, port):
        try:
            tn = self.telnet_mt(ip, port, 10)
            tn.read_until('>'.encode())
            tn.write('mtver'.encode() + b'\r\n')
            tn.read_until('>'.encode())
            tn.close()
            print('%s ��ȡ�汾��Ϣ�ɹ���' % ip)
        except:
            print('%s��ȡ�汾��Ϣ�ɹ�ʧ��' % ip)

    # ��ʾδ���ӳɹ��ն�
    def show_failed(self):
        count = 0
        print('�����ն��������')
        print('δ���ӳɹ��ն����£�')
        for j in self.ips:
            print(j)
            count += 1
        print('��%d̨' % count)

if __name__ == '__main__':
    start = Update()
    start.the_start()








