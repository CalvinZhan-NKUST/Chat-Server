# -*- coding: utf-8 -*-
import redis
import sys
import json
import requests
import configparser
import Model5000 as Model
import mqttNotification as mqttNotification
import execjs
import os
import subprocess
import bcrypt
import time
import logging 

from pymysql.converters import escape_string
from datetime import datetime,timezone,timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_  
from sqlalchemy import text


Session = Model.sessionmaker(bind=Model.DBLink)

r = redis.StrictRedis('localhost', encoding='utf-8', decode_responses=True)
config = configparser.ConfigParser()
config.read('config.ini')

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='SaveHisMsg.log', filemode='w', format=FORMAT)

def sendMsg(RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime):

    MsgMap={}
    MsgID=''
    MaxSN = r.get(RoomID+'MaxSN')
    if str(MaxSN)!='None':
        MsgID=str(int(MaxSN)+1)
    else:
        MsgID='1'
    r.set(RoomID + "MaxSN", MsgID)

    messageCache = config['ChatMessage']['MessageLeft']

    insertPosition=''
    if MsgID[-1]=='0':
        insertPosition = 10
    else:
        insertPosition = str(MsgID)[-1]

    print("insert位置："+str(insertPosition))
    print('MsgID:'+MsgID)

    MsgMap={
                'RoomID':RoomID,
                'MsgID':MsgID,
                'SendUserID':SendUserID,
                'SendName':SendName,
                'ReceiveName':ReceiveName,
                'ReceiveUserID':ReceiveUserID,
                'MsgType':MsgType,
                'Text':Text,
                'DateTime':DateTime   
            }
    jsonMsgMap = json.dumps(MsgMap, ensure_ascii=False)

    r.set(RoomID + "baseSN", int(MsgID)-10)
    
    print(jsonMsgMap)
    r.hmset(RoomID,{str(insertPosition):jsonMsgMap})
    notifyToClient(RoomID,Text,SendName,SendUserID,MsgID,'Message',MsgType)
    return MsgID

def getMsg(RoomID, MsgClientID, MsgPara):
    msgData = []
    messageCache = config['ChatMessage']['MessageLeft']
    MaxSN = r.get(RoomID + "MaxSN")
    getMsgResult = ''
    print('MsgClientID:'+MsgClientID)
    getMsgNum = 0
    targetMsgSN = 0
    if str(MaxSN)!='None':
        if str(MsgClientID)!='0':
            if str(MsgPara)=='1':
                if MsgClientID[-1]!='0':
                    getMsgResult = r.hget(RoomID,MsgClientID[-1])
                    if str(getMsgResult)!='None':
                        getMsgData = json.loads(getMsgResult)
                        msgData.append(getMsgData)
                else:
                    getMsgResult = r.hget(RoomID,10)
                    if str(getMsgResult)!='None':
                        getMsgData = json.loads(getMsgResult)
                        msgData.append(getMsgData)
            else:
                if int(MsgClientID)+int(MsgPara)>int(MaxSN):
                    targetMsgSN = MaxSN
                    print('目標訊息為MaxSN')
                else:
                    targetMsgSN = int(MsgClientID)+int(MsgPara)
                    print('目標訊息為MsgCLient+MsgPara')
                    if int(targetMsgSN) < (int(MaxSN)-int(messageCache)+1):
                        targetMsgSN = int(MaxSN)-int(messageCache)+int(MsgPara)
                        print('目標訊息為Max-Cache+MsgPara')

                print('目標訊息:'+str(targetMsgSN))
                if str(targetMsgSN)[-1]!='0':
                    print('準備取得訊息')
                    for i in range(int(str(targetMsgSN)[-1]),0,-1):
                        getMsgResult = r.hget(RoomID,i)
                        if str(getMsgResult)!='None':
                            if int(getMsgNum) < int(MsgPara):
                                print('正在取得第一部分訊息')
                                getMsgNum+=1
                                getMsgData = json.loads(getMsgResult)
                                msgData.append(getMsgData)
                    for j in range(int(messageCache),int(str(targetMsgSN)[-1]),-1):
                        getMsgResult = r.hget(RoomID,j)
                        if str(getMsgResult)!='None':
                            if int(getMsgNum) < int(MsgPara):
                                print('正在取得第二部分訊息')
                                getMsgNum+=1
                                getMsgData = json.loads(getMsgResult)
                                msgData.append(getMsgData)
                else:

                    print('Start:'+str(MsgClientID)[-1]+', End:'+str(targetMsgSN)[-1])
                    for j in range(int(messageCache), int(str(targetMsgSN)[-1]),-1):
                        getMsgResult = r.hget(RoomID,j)
                        if str(getMsgResult)!='None':
                            if int(getMsgNum) < int(MsgPara):
                                print('正在取得第三部分訊息')
                                getMsgNum+=1
                                getMsgData = json.loads(getMsgResult)
                                msgData.append(getMsgData)
        else:
            if MaxSN[-1]!='0':
                for i in range(int(MaxSN[-1]),0,-1):
                    getMsgResult = r.hget(RoomID,i)
                    if str(getMsgResult)!='None':
                        if int(getMsgNum) < int(MsgPara):
                            getMsgNum+=1
                            getMsgData = json.loads(getMsgResult)
                            msgData.append(getMsgData)
                for j in range(int(messageCache),int(MaxSN[-1]),-1):
                    getMsgResult = r.hget(RoomID,j)
                    if str(getMsgResult)!='None':
                        if int(getMsgNum) < int(MsgPara):
                            getMsgNum+=1
                            getMsgData = json.loads(getMsgResult)
                            msgData.append(getMsgData)
            else:
                for j in range(int(messageCache),0,-1):
                    getMsgResult = r.hget(RoomID,j)
                    if str(getMsgResult)!='None':
                        if int(getMsgNum) < int(MsgPara):
                            getMsgNum+=1
                            getMsgData = json.loads(getMsgResult)
                            msgData.append(getMsgData)

        return msgData 
    else:
        return msgData 

def notifyToClient(RoomID,Text,SendName,SendUserID, MsgID, notifiType, msgType):
    try:
        memberList = ''
        notifyMember = ''
        RoomMember = r.get('NotifyMembers_'+RoomID)
        
        if str(RoomMember)=='None':
            session = Session()
            result = session.query(Model.chatInfo).filter(Model.chatInfo.RoomID==RoomID)
            for i in result:
                memberList += i.UserID +','
            session.close()
            print('memeberList:'+memberList)
            r.set('NotifyMembers_'+RoomID, memberList)
            RoomMember = r.get('NotifyMembers_'+RoomID)

        print('RoomID:'+RoomID)
        print('RoomMember:'+RoomMember)
        for i in RoomMember:
            if i in ',':
                if str(notifyMember)!=str(SendUserID):
                    Topic = 'User_'+notifyMember+"/"+RoomID
                    print("mqtt Notify")
                    mqttNotification.sendNotify(Topic, RoomID, MsgID, SendName, Text, notifiType, SendUserID, msgType)
                    
                getToken = r.get('UserToken_'+notifyMember)
                print('UserID:'+notifyMember)
                print('getToken:'+str(getToken))
                if str(getToken)!='None' and str(notifyMember)!=str(SendUserID):
                    cmd = "python3 PushApns.py "+str(getToken)+" \'"+Text+"\' "+SendName+" "+str(RoomID)+" "+str(MsgID)+" "+str(SendUserID)+" "+ msgType
                    subprocess.Popen(cmd, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                notifyMember = ''
            else:
                notifyMember = notifyMember+i
    except:
        print('notifyToClient Err:',sys.exc_info()[0])

# 重新設定聊天室內要通知的使用者
def resetRoomMember(RoomID):
    session = Session()
    memberList = ''
    result = session.query(Model.chatInfo).filter(Model.chatInfo.RoomID==RoomID)
    for i in result:
        memberList += i.UserID +','
    session.close()
    print('memeberList:'+memberList)
    r.set('NotifyMembers_'+RoomID, memberList)
    RoomMember = r.get('NotifyMembers_'+RoomID)
    return 'ok'

# 通知使用者被新增到校新創的聊天室
def updateRoomNum(UserIDList, RoomType, newRoomID, addUserID):
    UserID = ''
    MsgID=0
    Text = ''
    SendName='New chat room!'
    print(UserIDList)
    print('執行聊天室數量增加')
    for i in UserIDList:
        if i in ',':
            if RoomType=='1':
                Text = '您被加入至新的聊天室'
            elif RoomType=='2':
                Text = '您被加入至新的群組'                    

            getToken = r.get('UserToken_'+UserID)
            if str(getToken)!='None':
                if str(UserID) != str(addUserID):
                    print('準備通知Apns')
                    print(str(getToken))
                    cmd = "python3 PushApns.py "+str(getToken)+" \'"+Text+"\' \'"+SendName+"\' "+str(newRoomID)+" "+str(MsgID)+" "+str(addUserID)+" "+" NewRoom"
                    print(cmd)
                    subprocess.Popen(cmd, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
            
            Topic = 'User_'+UserID+"/"+newRoomID
            if str(UserID) != str(addUserID):
                print('準備通知MQTT')
                command = "python3 mqttNotification.py " +str(Topic)+" "+str(newRoomID)+" "+str(MsgID)+" \'"+str(SendName)+"\' \'"+str(Text)+"\' NewRoom "+str(addUserID)+" \'NewRoom\'"
                subprocess.Popen(command, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                print(str(Topic))
            UserID = ''
        else:
            UserID += i
    return 'ok'

def notification(RoomIDList):
    try:
        RoomID = ''
        notifyGet = {}
        notifyRes = []
        for i in RoomIDList:
            if i in ',':
                getMaxSN=r.get(RoomID + "MaxSN")
                if str(getMaxSN)!='None':
                    notifyGet={'RoomID':RoomID,'MaxSN':getMaxSN}
                else:
                    notifyGet={'RoomID':RoomID,'MaxSN':'0'}
                notifyRes.append(notifyGet)
                RoomID=''
            else:
                RoomID += i
    except:
        print('notification Err:',sys.exc_info()[0])

    return notifyRes

# 儲存iOS用戶的APNs Token
def saveUserToken(UserID, Token):
    try:
        print('取得的UserID:'+UserID+", Token:"+Token)
        r.set('UserToken_'+UserID,Token)
    except:
        print('saveUserToken Err:',sys.exc_info()[0])
    return 'ok'

def compareToken(UserID,Token):
    try:
        format_pattern = "%Y-%m-%d %H:%M:%S"
        
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
        serverTime = str(dt2.strftime(format_pattern))

        tokenTime = Token[-13:]
        print(Token[-13:])

        tokenTimeTransfer = get_formattime_from_timestamp(int(tokenTime)/1000)

        difference = (datetime.strptime(serverTime, format_pattern) - datetime.strptime(tokenTimeTransfer, format_pattern))
        dayTimeGap = int(difference.days)
        
        if dayTimeGap > 10:
            print(dayTimeGap)
            return 'denied'

        checkToken = Token.split(str(tokenTime),1)
        compareUser = 'UserID_'+str(UserID)
        if bcrypt.checkpw(compareUser.encode('utf8'),checkToken[0].encode('utf8')):
            return 'pass'
        else:
            return 'denied'
    except:
        print('tokenCompare Err:',sys.exc_info()[0])
        return 'denied'

def get_formattime_from_timestamp(time_stamp):
    format_pattern = "%Y-%m-%d %H:%M:%S"
    date_array = datetime.fromtimestamp(time_stamp)
    time_str = date_array.strftime(format_pattern)
    return time_str