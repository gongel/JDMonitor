from email.header import Header
from email.mime.application import MIMEApplication
import datetime
from email.utils import parseaddr, formataddr

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#如果邮件地址包含中文，需要通过Header对象进行编码
class Mail():
    def _format_addr(self,s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def SendMailFile(self,filename,MessageSource,FromUserName,FileSize,CreatTime):
        CreatTime=datetime.datetime.fromtimestamp(CreatTime)
        FileSize=int(FileSize)
        if FileSize>1024**3:
            FileSize=str(FileSize/(1024**3))+'GB'
        elif FileSize>1024**2:
            FileSize=str(FileSize/(1024**2))+'MB'
        elif FileSize>1024:
            FileSize=str(FileSize/(1024))+'KB'
        else:
            FileSize=str(FileSize)+'B'
        sender = '**@163.com'
        passWord = '**'
        mail_host = 'smtp.163.com'
        # receivers是邮件接收人，用列表保存，可以添加多个
        receivers = ['**@qq.com']

        # 设置email信息
        msg = MIMEMultipart()
        # 邮件主题
        msg['Subject'] = Header('WeChat File','utf-8').encode()
        # 发送方信息
        msg['From'] = self._format_addr('Admin')
        # 邮件正文是MIMEText:
        msg_content = '已收到微信文件，请马上查看！详情如下：\n来源：{}\n发送者：{}\n文件名：{}\n大小：{}\n发送时间：{}\n'.format(MessageSource,FromUserName,filename,FileSize,CreatTime)
        # 简单文本到正文，plain
        msg.attach(MIMEText(msg_content, 'plain', 'utf-8'))
        # # 将附件图片嵌入正文，html
        # msg.attach(MIMEText('<html><body><h1>尽快扫码吧！</h1>' + '<p><img src="cid:0"></p>' + '</body></html>', 'html', 'utf-8'))

        # 添加附件方法一（基本不可取）
        # with open(filename,'rb') as f:
        #     mime = MIMEBase('application','octet-stream')
        #     # 加上必要的头信息:
        #     mime.add_header('Content-Disposition', 'attachment', filename=filename)#中文名乱码，英文名没问题，文件内容乱码
        #     # mime.add_header('Content-Disposition', 'attachment', filename=('gbk','',filename))#只是文件内容乱码
        #     # mime.add_header('Content-Disposition', 'attachment', filename="%s"%os.path.basename(filename))#中文名乱码，另外内容都乱码
        #     mime.set_payload(f.read())
        #     encoders.encode_base64(mime)
        #     # 添加到MIMEMultipart:
        #     msg.attach(mime)

        # 添加附件方法二
        with open(filename,'rb') as f:
            mime=MIMEApplication(f.read())
            # mime.add_header('Content-Disposition', 'attachment', filename=('gbk','',filename))   gbk,utf-8,unicode遇到中文直接报错
            # mime.add_header('Content-Disposition', 'attachment', filename=filename)#中文名 tcmime.2344.2546.20297.bin
            mime.add_header('Content-Disposition', 'attachment', filename="%s"%Header(filename,'utf-8').encode())#成功
            msg.attach(mime)

        # 登录并发送邮件
        try:
            # 163smtp服务器的端口号为465或
            s = smtplib.SMTP_SSL("smtp.163.com", 465)
            s.set_debuglevel(1)
            s.login(sender, passWord)
            # 给receivers列表中的联系人逐个发送邮件
            for item in receivers:
                msg['To'] = to =self._format_addr(item)
                s.sendmail(sender, to, msg.as_string())
                # print('Success!')
            s.quit()
            # print("All emails have been sent over!")
        except smtplib.SMTPException as e:
            print("Falied,%s", e)

    def SendMailMessage(self,content):
        sender = '**@163.com'
        passWord = '**'
        mail_host = 'smtp.163.com'
        # receivers是邮件接收人，用列表保存，可以添加多个
        receivers = ['**@qq.com']

        # 设置email信息
        msg = MIMEMultipart()
        # 邮件主题
        msg['Subject'] = Header('JD Monitor','utf-8').encode()
        # 发送方信息
        msg['From'] = self._format_addr('Admin')
        # 邮件正文是MIMEText:
        msg_content =content
        # 简单文本到正文，plain
        msg.attach(MIMEText(msg_content, 'plain', 'utf-8'))

        # 登录并发送邮件
        try:
            # 163smtp服务器的端口号为465或
            s = smtplib.SMTP_SSL("smtp.163.com", 465)
            s.set_debuglevel(1)
            s.login(sender, passWord)
            # 给receivers列表中的联系人逐个发送邮件
            for item in receivers:
                msg['To'] = to =self._format_addr(item)
                s.sendmail(sender, to, msg.as_string())
            s.quit()
        except smtplib.SMTPException as e:
            print("Falied,%s", e)