# -*- coding: utf-8 -*-
import redis
import sys
import json
import requests
import configparser
import Model5000 as Model
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

    if(MsgID==1):
        r.set(RoomID + "baseSN", MsgID)

    baseSN=r.get(RoomID+"baseSN")
    changeBase = int(baseSN) + 10
    
    if(MsgID==changeBase):
        r.set(RoomID + "baseSN", MsgID)

    
    print(jsonMsgMap)
    r.hmset(RoomID,{str(insertPosition):jsonMsgMap})
    notifyToApns(RoomID,Text,SendName,SendUserID)


    return MsgID


def getMsg(RoomID, MsgClientID, MsgPara):
    msgData = []
    messageCache = config['ChatMessage']['MessageLeft']
    baseSN = r.get(RoomID + "baseSN")
    MaxSN = r.get(RoomID + "MaxSN")
    getMsgResult = ''
    
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
        if MaxSN[-1]!='0':
            getMsgResult = r.hget(RoomID,MaxSN[-1])
            if str(getMsgResult)!='None':
                getMsgData = json.loads(getMsgResult)
                msgData.append(getMsgData)
        else:
            getMsgResult = r.hget(RoomID,10)
            if str(getMsgResult)!='None':
                getMsgData = json.loads(getMsgResult)
                msgData.append(getMsgData)
    return msgData    



# def getMsg(RoomID, MsgClientID, MsgPara): 
#     try:
#         msgData = []
#         messageCache = config['ChatMessage']['MessageLeft']
#         baseSN = r.get(RoomID + "baseSN")
#         MaxSN = r.get(RoomID + "MaxSN")
#         MsgID = 0

#         if str(MaxSN)!='None':
#             MsgIDCache = int(MaxSN) - int(MsgPara)
#             if int(MsgClientID) < int(MsgPara):
#                 MsgID = int(MsgIDCache)
#             else:
#                 MsgID = int(MsgClientID)

#             if (int(MsgID) < int(baseSN)):
#                 getNewMsgPosition = int(MaxSN) - int(baseSN) + 1
#                 print("baseSN:" + str(baseSN))
#                 print("MsgID:"+ str(MsgID))
#                 getPosition = int(baseSN) - int(MsgID) - 1
#                 print('MsgID<=Base')
#                 print("getPos:" + str(getPosition))
#                 for n in range(getPosition,0,-1):
#                     getMsgResult = r.hget(RoomID,n)
#                     if str(getMsgResult)!='None':
#                         getMsgData = json.loads(getMsgResult)
#                         msgData.append(getMsgData)
                
#                 for m in range(int(messageCache),int(messageCache)-getNewMsgPosition,-1):
#                     getMsgResult = r.hget(RoomID,m)
#                     if str(getMsgResult)!='None':
#                         getMsgData = json.loads(getMsgResult)
#                         msgData.append(getMsgData)

#             else:
#                 getPosition = int(messageCache) - (int(MsgID) - int(baseSN))-1
#                 print('MsgID=>Base')
#                 print("getPos:" + str(getPosition))
#                 endMsgPosition = int(MaxSN)-int(MsgID)
#                 for i in range(getPosition,(getPosition-endMsgPosition),-1):
#                     getMsgResult = r.hget(RoomID,i)
#                     if str(getMsgResult)!='None':
#                         getMsgData = json.loads(getMsgResult)
#                         msgData.append(getMsgData)
#         else:
#             msgData='none'
#     except:
#         print('getMsg Err:',sys.exc_info()[0])

#     return msgData    

def notification(RoomIDList):
    try:
        RoomID = ''
        notifyGet = {}
        notifyRes = []
        for i in RoomIDList:
            # print('i:'+i)
            if i in ',':
                # print('getRoomID:'+RoomID)
                getMaxSN=r.get(RoomID + "MaxSN")
                # print('MaxSN:'+str(getMaxSN))
                if str(getMaxSN)!='None':
                    notifyGet={'RoomID':RoomID,'MaxSN':getMaxSN}
                else:
                    notifyGet={'RoomID':RoomID,'MaxSN':'0'}
                notifyRes.append(notifyGet)
                RoomID=''
            else:
                RoomID += i
        # roomMaxSN = r.get(RoomID+'MaxSN')
    except:
        print('notification Err:',sys.exc_info()[0])

    return notifyRes

def notifyToApns(RoomID,Text,SendName,SendUserID):
    try:
        memberList = ''
        apnsMember = ''
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
                getToken = r.get('UserToken_'+apnsMember)
                print('UserID:'+apnsMember)
                print('getToken:'+str(getToken))
                if str(getToken)!='None' and str(apnsMember)!=str(SendUserID):
                    # apns(str(getToken),Text,SendName)
                    cmd = "python3 PushApns.py "+str(getToken)+" "+Text+" "+SendName
                    subprocess.Popen(cmd, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                apnsMember = ''
            else:
                apnsMember = apnsMember+i
    except:
        print('notifyToApns Err:',sys.exc_info()[0])

def apns(tokenID, text, sendName):
    try:
        ctx = execjs.compile("""
        var fs = require('fs');
        var jwt = require('jsonwebtoken');

        function apns(tokenID, text, sendName){
            var epochtime = Date.now() / 1000 
            var cert = fs.readFileSync('AuthKey_7Q7CZ5PDJH.p8');  // get private key
            var token = jwt.sign({
                "iss": "CXB28GPWN9",
                "iat": parseInt(epochtime)}, cert, { header: {"alg": "ES256", "kid": "7Q7CZ5PDJH"}, algorithm: 'ES256'});
            console.log(tokenID)

            var apn = require('apn');

            var options = {
            token: {
                key: "AuthKey_7Q7CZ5PDJH.p8",
                keyId: "7Q7CZ5PDJH",
                teamId: "CXB28GPWN9"
            },
            production: true
            };

            var apnProvider = new apn.Provider(options);
            var note = new apn.Notification();
            let deviceToken = tokenID;

            note.category = "MEETING_INVITATION";
            note.title = sendName;
            note.body = text;
            note.sound = "default";
            note.badge = 1;
            note.setAction("MEETING_INVITATION").setMutableContent(1);
            note.contentAvailable = 1;	
            note.topic = "com.nkust.flutterMessenger";

            apnProvider.send(note, deviceToken).then( (result) => {
                process.exit();
                // see documentation for an explanation of result
            });
        }
        """)
        ctx.call("apns", tokenID, text, sendName)
        print('send Notify')
    except:
        print('apns Err:',sys.exc_info()[0])


def saveUserToken(UserID, Token):
    try:
        print('取得的UserID:'+UserID+", Token:"+Token)
        r.set('UserToken_'+UserID,Token)
    except:
        print('saveUserToken Err:',sys.exc_info()[0])

    return 'ok'

def setUUID(UserID,UUID):
    r.set(UserID+"_uuid",UUID)

def compareUUID(UserID,UUID):
    compareResult = r.get(UserID+"_uuid")
    if str(compareResult)!='None':
        if str(UUID)==str(compareResult):
            return 'pass'
        else:
            return 'denied'
    else:
        return 'denied'