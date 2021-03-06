import telnetlib


def allupdate(ip, sendFilename):
    Host = ip
    username = 'admin'
    password = 'admin'
    commands = ['she', 'cd ramdisk', 'allupdate %s'% sendFilename, 'reboot']

    try:
        tn = telnetlib.Telnet(Host, port=23, timeout=200)
        tn.set_debuglevel(5)
    except:
        print('%s无法打开telnet连接'% ip)
    try:
        tn.read_until('Username:'.encode())
        tn.write(username.encode('ascii') +b'\r\n' )   # 输入用户名
        tn.read_until('Password:'.encode())
        tn.write(password.encode('ascii')+b'\r\n' )     # 输入密码
        print('%s正在升级请稍后...'% ip)
        tn.read_until('#'.encode())          # 检测到Router#就输入命令
        for command in commands:
            tn.write(command.encode('ascii')+b'\r\n')
        info = tn.read_all()
        print(info)

        tn.read_until('#'.encode())
        tn.close()              # 关闭连接
    except:
        print('%s telnet连接失败...'% ip)
if __name__ == '__main__':      # 调试使用
    ip = '172.16.48.88'
    sendFilename = 'h900.bin.gz'
    allupdate(ip, sendFilename)
