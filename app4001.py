# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from mqttNotification import sendNotify
from datetime import datetime,timezone,timedelta
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from pymysql.converters import escape_string
import saveHistoryMsg as saveHisMsg
import Controller4000 as Controller
import time
import redis
import configparser
import logging
import subprocess
import sys
import json
import uuid
import os

db = SQLAlchemy()
app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config["DataBase"]["SQLALCHEMY_TRACK_MODIFICATIONS"]
app.config['SQLALCHEMY_DATABASE_URI'] = config["DataBase"]["SQLALCHEMY_DATABASE_URI"]+'?charset=utf8mb4'
db.init_app(app)

r = redis.StrictRedis('localhost', encoding='utf-8', decode_responses=True)

ALLOWD_EXTENSIONS = set(['jpeg','jpg','png','mp4'])

# 送訊息
@app.route("/send", methods=["POST"]) 
def sendMsg():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    request_send = request.values
    print(request.values)
    RoomID = request_send['RoomID']
    SendUserID = request_send['SendUserID']
    MsgType = request_send['MsgType']
    SendName = request_send['SendName']
    ReceiveName = request_send['ReceiveName']
    ReceiveUserID = request_send['ReceiveUserID']
    Text = request_send['Text']
    Token = request_send['Token']
    DateTime = str(dt2.strftime("%Y-%m-%d %H:%M:%S"))

    compareRes = Controller.compareToken(SendUserID,Token)

    if str(compareRes) == 'pass':
        getMsgID = Controller.sendMsg(RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime)
        text_insert = Text.replace('%','%%')
        mysql_insert = escape_string(text_insert)
        print(mysql_insert)
        sql_insert = "INSERT INTO "+ RoomID +"msgList(MsgID, RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime) VALUES ("+getMsgID+", "+RoomID+", "+ SendUserID+", \'"+ SendName +"\', \'"+ReceiveName+"\', "+ReceiveUserID+", \'"+MsgType+"\', \'"+mysql_insert+"\', \'"+DateTime+"\')"
        res = db.engine.execute(sql_insert)

        saveResult = saveHisMsg.saveHistoryMessage(getMsgID, RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime)
        resMsgID = {'MsgID':getMsgID, 'LastMsgTime':DateTime}
        return json.dumps(resMsgID, ensure_ascii=False)
    else:
        return 'Token驗證失敗'

# 收訊息
@app.route("/getMsg", methods=["POST"])
def getMsg():
    request_getMsg = request.values
    RoomID = request_getMsg['RoomID']
    MsgID = request_getMsg['MsgID']
    MsgPara = request_getMsg['MsgPara']
    Token = request_getMsg['Token']
    UserID = request_getMsg['UserID']

    compareRes = Controller.compareToken(UserID,Token)
    if str(compareRes) == 'pass':
        getMsgRes = Controller.getMsg(RoomID, MsgID, MsgPara)
        MsgList = {'res':getMsgRes} 
        return json.dumps(MsgList, ensure_ascii=False).encode('utf8') 
    else:
        return 'Token驗證失敗'

# 查詢聊天室目前訊息編號
@app.route("/notify", methods=["POST"])
def notify():
    # 要改成一個List來查詢RoomID的MaxSN
    request_notify = request.values
    print(request_notify)
    UserID = request_notify['UserID']
    Token = request_notify['Token']
    RoomIDList = request_notify['RoomIDList']
    print(RoomIDList)
    
    compareRes = Controller.compareToken(UserID,Token)
    if str(compareRes) == 'pass':
        notifyRes = Controller.notification(RoomIDList)
        notifyList = {'res':notifyRes}
        return json.dumps(notifyList, ensure_ascii=False)
    else:
        return 'Token驗證失敗'
        
# 儲存iOS用戶的APNs Token
@app.route("/saveToken", methods=["POST"])
def report():
    request_saveToken = request.values
    UserID = request_saveToken['UserID']
    TokenUser = request_saveToken['ChatServerToken']
    Token = request_saveToken['Token']

    compareRes = Controller.compareToken(UserID,TokenUser)
    if str(compareRes) == 'pass':
        saveResult = Controller.saveUserToken(UserID,Token)
    else:
        saveResult = 'Token驗證失敗'

    return saveResult

# 檢查token，是否能夠持續登入
@app.route("/keepLogin", methods=["POST"])
def keepLogin():
    request_keepLogin = request.values
    UserID = request_keepLogin['UserID']
    Token = request_keepLogin['Token']
    result = Controller.compareToken(UserID,Token)
    if str(result)!='denied':
        tokenTimeStamp = int(round(time.time()*1000))
        tokenTime = Token[-13:]
        checkToken = Token.split(str(tokenTime),1)
        refreshToken = str(checkToken[0]) + str(tokenTimeStamp)
        compareResult = {'res':result,'Token':refreshToken}
    else:
        compareResult = {'res':result}

    return json.dumps(compareResult, ensure_ascii=False).encode('utf8')

# 檔案上傳
@app.route("/uploadFiles", methods=["POST"])
def uploadFiles():
    request_uploadFiles = request.values
    UserID = request_uploadFiles['UserID']
    Token = request_uploadFiles['Token']
    FileType = request_uploadFiles['FileType']

    compareRes = Controller.compareToken(UserID,Token)
    if str(compareRes) == 'pass':
        if 'File' not in request.files:
            return '並未上傳任何檔案'
        fileUpload = request.files['File']
        if fileUpload.filename== '':
            return '未上傳檔案名稱'
        if fileUpload and allowed_file(fileUpload.filename):
            print(fileUpload.filename)
            if FileType=='Image':
                fileID = uuid.uuid1()
                newFileName = str(fileID) + '.jpg'
                fileUpload.save(os.path.join(config['Server']['imagePath'], newFileName))
                fileUploadRes = config['ChatMessage']['imageURL'] + newFileName
                return fileUploadRes
            elif FileType=='Video':
                fileID = uuid.uuid1()
                newFileName = str(fileID) + '.mp4'
                fileUpload.save(os.path.join(config['Server']['videoPath'], newFileName))
                fileUploadRes = config['ChatMessage']['videoURL'] + newFileName
                return fileUploadRes
            else:
                return 'Wrong Type !'
        else:
            print(allowed_file(fileUpload))
            return '檔案已被拒絕'
    else:
        return 'Token驗證失敗'
        
# 副檔名驗證
def allowed_file(FileName):
    return '.' in FileName and \
        FileName.rsplit('.', 1)[1] in ALLOWD_EXTENSIONS

@app.route("/notifyToClient", methods=["POST"])
def notifyToClient():
    request_notifyToClient = request.values
    RoomID = request_notifyToClient['RoomID']
    Text = request_notifyToClient['Text']
    SendName = request_notifyToClient['SendName']
    SendUserID = request_notifyToClient['SendUserID']
    MsgID = request_notifyToClient['MsgID']
    NotifiType = request_notifyToClient['NotifyType']
    MsgType = request_notifyToClient['MsgType']
    notifyToClientRes = notifyToClient(RoomID,Text,SendName,SendUserID, MsgID, NotifiType, MsgType)
    return 'ok'

if __name__ == "__main__":
    portNumber = str(sys.argv[1])
    app.run(host=config['Server']['server_ip'],port=portNumber, threaded=True)
    # handler = logging.FileHandler('flask.log', encoding='UTF-8')
    # handler.setLevel(logging.ERROR) 
    # logging_format = logging.Formatter(
    #     '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    # handler.setFormatter(logging_format)
    # app.logger.addHandler(handler)
    # app.run(ssl_context=('ceca.crt', 'private.key'),host=config['Server']['server_ip'],
    # port=config['Server']['portForRedis'],threaded=True)
    
