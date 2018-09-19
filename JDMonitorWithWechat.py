# -*- coding: UTF-8 -*-
import  re
import itchat
import requests
from itchat.content import ATTACHMENT, TEXT
import Monitor
import Mail

mail=Mail.Mail()

#以下是监控微信聊天文件的转发
@itchat.msg_register([ATTACHMENT],isFriendChat=True,isGroupChat=True)
def download_files_and_forward(msg):
    msg.download(msg.fileName)
    r = re.match('(@@)(.*)', msg['FromUserName'])
    if r:
        MessageSource = '群聊'
        mail.SendMailFile(msg.fileName, MessageSource, msg['ActualNickName'] + '(' +
                 itchat.search_chatrooms(userName=msg['FromUserName'])['NickName'] + ')', msg['FileSize'],
                 msg['CreateTime'])

    else:
        MessageSource = '个人'
        mail.SendMailFile(msg.fileName, MessageSource, itchat.search_friends(userName=msg['FromUserName'])['NickName'] + '(' +
                 itchat.search_friends(userName=msg['FromUserName'])['RemarkName'] + ')', msg['FileSize'],
                 msg['CreateTime'])

@itchat.msg_register([TEXT])
def msg_receive(msg):
    if itchat.search_friends(userName=msg['FromUserName'])['NickName']=='**':#** 为你的微信昵称
        list=msg['Content'].split()
        price = None
        clock =int(5)
        if len(list)>0:
            id=list[0][3:]
        else:
            id=None
        if len(list)==3:
            price=list[1][6:]
            clock=int(list[2][6:])
        elif len(list)==2:
            if list[1][:5]=='price':
                price = list[1][6:]
            elif list[1][:4]=='clock':
                clock = int(list[2][6:])
        if len(list)>0 and list[0][:2]=='id' and id != None:
            monitor = Monitor.Monitor(sess=requests.Session(), stock_id=id,price=price,area_id='2_2830_51800_0',clock=clock)
            monitor.good_detail_loop()
itchat.auto_login(enableCmdQR=2,picDir='/root/QR.png',hotReload=False)
# itchat.auto_login(hotReload=True)
itchat.run()
