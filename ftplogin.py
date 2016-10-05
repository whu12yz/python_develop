from ftplib import FTP
import os
import telnet_login
import threading                # 线程
# from multiprocessing.dummy import Pool  # 线程


def getip(i):                                                                    # 获取ip地址以及文件名称
    path = os.path.join(os.path.expanduser("~"), 'Desktop//')
    cwdsend = 'ramdisk'
    ip = input('请输入第%s个终端ip地址:' % i)
    sendFilename = input('请输入升级包名称并将其放置于桌面：')
    return ip, cwdsend, sendFilename, path


def getfilename(ip, cwd):                                           # 获取文件名
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


def getfile(ip, cwd, filename, path):                    # ftp下载文件，从服务器下载文件
    try:
        ftp = FTP()
        timeout = 30
        port = 21
        ftp.connect(ip, port, timeout)
        ftp.login('admin', 'admin')

        print(ftp.getwelcome())
        ftp.cwd(cwd)
        list = ftp.nlst()
        for name in list:
            print(name)

        ftp.retrbinary('RETR '+filename, open(path + filename,'wb').write)
        ftp.quit()
    except:
        print('%s下载文件失败...' % ip)


def sendfile(ip,cwd, sendFilename, path):              # 上传文件
    try:
        ftp = FTP()
        timeout = 10
        port = 21
        ftp.connect(ip, port, timeout)
        ftp.login('admin', 'admin')

        print(ftp.getwelcome())
        ftp.cwd(cwd)
        print('%s ramdisk中已有文件如下:'% ip)
        list = ftp.nlst()
        for name in list:
            print(name)
        print('%s开始上传 ...'% ip)
        ftp.storbinary('STOR '+sendFilename, open(path+sendFilename, 'rb'))
        print('%s 升级文件上传成功，正在升级...'% ip)
        ftp.quit()
    except:
        print('%s连接超时...'% ip)


def mainfunc(ip, cwdsend, sendFilename, path):                          # 调用上传文件、升级函数

    sendfile(ip, cwdsend, sendFilename, path)
    getfilename(ip, cwdsend)
    telnet_login.allupdate(ip, sendFilename)

def the_start():
    threads = []
    names = locals()
    print('Welcome!!!')
    mtn = int(input('请输入想要升级的终端个数：'))
    for i in range(0, mtn):
        names['p%s' % i], cwdsend, names['sendFilename%s' % i], path = getip(i+1)
        names['t%s' % i] = threading.Thread(target=mainfunc, args=(names['p%s' % i], cwdsend, names['sendFilename%s' % i], path))
        threads.append(names['t%s' % i])
    for t in threads:
        t.start()
    t.join()

if __name__ == '__main__':
    the_start()



