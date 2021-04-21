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

from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_  
from sqlalchemy import text


Session = Model.sessionmaker(bind=Model.DBLink)

r = redis.StrictRedis('localhost', encoding='utf-8', decode_responses=True)
config = configparser.ConfigParser()
config.read('config.ini')

def sendMsg(RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime):

    MsgMap={}
    MsgID=''
    MaxSN = r.get(RoomID+'MaxSN')
    if str(MaxSN)!='None':
        MsgID=str(int(MaxSN)+1)
    else:
        MsgID='1'

    messageCache = config['ChatMessage']['MessageLeft']
    r.set(RoomID + "MaxSN", MsgID)

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
    notifyToApns(RoomID,Text,SendName,SendUserID,MsgID)
    return MsgID


def getMsg(RoomID, MsgClientID, MsgPara):
    msgData = []
    messageCache = config['ChatMessage']['MessageLeft']
    MaxSN = r.get(RoomID + "MaxSN")
    getMsgResult = ''
    
    if str(MaxSN)!='None':
        if str(MsgPara)=='10':
            if MaxSN[-1]!='0':
                for i in range(int(MaxSN[-1]),0,-1):
                    getMsgResult = r.hget(RoomID,i)
                    if str(getMsgResult)!='None':
                        getMsgData = json.loads(getMsgResult)
                        msgData.append(getMsgData)
                for j in range(int(messageCache),int(MaxSN[-1]),-1):
                    getMsgResult = r.hget(RoomID,j)
                    if str(getMsgResult)!='None':
                        getMsgData = json.loads(getMsgResult)
                        msgData.append(getMsgData)
            else:
                for j in range(int(messageCache),0,-1):
                    getMsgResult = r.hget(RoomID,j)
                    if str(getMsgResult)!='None':
                        getMsgData = json.loads(getMsgResult)
                        msgData.append(getMsgData)
        elif str(MsgPara)=='1':
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
        return msgData 
    else:
        return msgData 

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

def notifyToApns(RoomID,Text,SendName,SendUserID, MsgID):
    try:
        memberList = ''
        notifyMember = ''
        RoomMember = r.get('NotifyApns_'+RoomID)
        
        if str(RoomMember)=='None':
            session = Session()
            result = session.query(Model.chatInfo).filter(Model.chatInfo.RoomID==RoomID)
            for i in result:
                memberList += i.UserID +','
            session.close()
            print('memeberList:'+memberList)
            r.set('NotifyApns_'+RoomID, memberList)

        RoomMember = r.get('NotifyApns_'+RoomID)
        print('RoomID:'+RoomID)
        print('RoomMember:'+RoomMember)
        for i in RoomMember:
            if i in ',':
                
                if str(notifyMember)!=str(SendUserID):
                    Topic = 'User_'+notifyMember+"/"+RoomID
                    # mqttNotification.sendNotify(Topic,RoomID,MsgID,SendName,Text)
                    command = "python3 mqttNotification.py " +str(Topic)+" "+str(RoomID)+" "+str(MsgID)+" "+str(SendName)+" "+str(Text)+" Message"
                    subprocess.Popen(command, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

                getToken = r.get('UserToken_'+notifyMember)
                print('UserID:'+notifyMember)
                print('getToken:'+str(getToken))
                if str(getToken)!='None' and str(notifyMember)!=str(SendUserID):
                    # apns(str(getToken),Text,SendName)
                    cmd = "python3 PushApns.py "+str(getToken)+" "+Text+" "+SendName+" "+RoomID
                    subprocess.Popen(cmd, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                notifyMember = ''
            else:
                notifyMember = notifyMember+i
    except:
        print('notifyToApns Err:',sys.exc_info()[0])

def saveUserToken(UserID, Token):
    try:
        print('取得的UserID:'+UserID+", Token:"+Token)
        r.set('UserToken_'+UserID,Token)
    except:
        print('saveUserToken Err:',sys.exc_info()[0])

    return 'ok'

def setUUID(UserID,UUID):
    r.set(UserID+"_uuid",UUID)

def setUserRoomNum(UserID, RoomNum):
    r.set(UserID+"_RoomNum",RoomNum)
    return 'ok'

def updateRoomNum(UserIDList, RoomType, newRoomID, addUserID):
    UserID = ''
    MsgID=0
    Text = ''
    SendName='New chat room!'
    for i in UserIDList:
        if i in ',':
            roomNum = r.get(UserID+"_RoomNum")
            if str(roomNum)!='None':
                newRoomNum = int(roomNum)+1
                r.set(UserID+"_RoomNum", str(newRoomNum))
                Topic = 'User_'+UserID+"/NewRoom"
                if RoomType=='1':
                    Text = '您被加入至新的聊天室'
                elif RoomType=='2':
                    Text = '您被加入至新的群組'                    

                getToken = r.get('UserToken_'+notifyMember)
                if str(getToken)!='None' & UserID!=addUserID :
                    cmd = "python3 PushApns.py "+str(getToken)+" "+Text+" "+SendName+" "+newRoomID
                    subprocess.Popen(cmd, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                
                if UserID != addUserID:
                    command = "python3 mqttNotification.py " +str(Topic)+" "+str(newRoomID)+" "+str(MsgID)+" "+str(SendName)+" "+str(Text)+" NewRoom"
                    subprocess.Popen(command, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        else:
            UserID += i
    

def getRoomNum(UserID):
    roomNum = r.get(UserID+"_RoomNum")
    return str(roomNum)

def compareUUID(UserID,UUID):
    compareResult = r.get(UserID+"_uuid")
    if str(compareResult)!='None':
        if str(UUID)==str(compareResult):
            return 'pass'
        else:
            return 'denied'
    else:
        return 'denied'
