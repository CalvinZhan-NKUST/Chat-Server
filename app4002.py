# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import configparser
import sys
import json
import logging
import Controller4000 as Controller
from mqttPub import sendNotify
from datetime import datetime,timezone,timedelta


db = SQLAlchemy()

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config["DataBase"]["SQLALCHEMY_TRACK_MODIFICATIONS"]
app.config['SQLALCHEMY_DATABASE_URI'] = config["DataBase"]["SQLALCHEMY_DATABASE_URI"]

db.init_app(app)

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
    DateTime = str(dt2.strftime("%Y-%m-%d %H:%M:%S"))
    # sendMqtt = sendNotify(RoomID, SendName, Text[0:10])
    
    getMsgID = Controller.sendMsg(RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime)
    sql_insert = 'INSERT INTO  {RoomID_Table}msgList(MsgID, RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime) VALUES({MsgID_insert}, {RoomID_insert}, {SendUserID_insert}, "'"{SendName_insert}"'", "'"{ReceiveName_insert}"'", {ReceiveUserID_insert}, "'"{MsgType_insert}"'", "'"{Text_insert}"'", "'"{DateTime_insert}"'")'.format(RoomID_Table = RoomID, MsgID_insert = getMsgID, RoomID_insert = RoomID, SendUserID_insert = SendUserID, SendName_insert = SendName, ReceiveName_insert = ReceiveName, ReceiveUserID_insert = ReceiveUserID, MsgType_insert = MsgType,Text_insert = Text, DateTime_insert = DateTime)
    query_data = db.engine.execute(sql_insert)
    # print(sendMqtt)
    resMsgID = {'MsgID':getMsgID}

    return json.dumps(resMsgID, ensure_ascii=False)

# 收訊息
@app.route("/getMsg", methods=["POST"])
def getMsg():
    request_getMsg = request.values
    RoomID = request_getMsg['RoomID']
    MsgID = request_getMsg['MsgID']
    MsgPara = request_getMsg['MsgPara']
    getMsgRes = Controller.getMsg(RoomID, MsgID, MsgPara)
    MsgList = {'res':getMsgRes}  
    return json.dumps(MsgList, ensure_ascii=False).encode('utf8')

# 推播通知
@app.route("/notify", methods=["POST"])
def notify():
    # 要改成一個List來查詢RoomID的MaxSN
    request_notify = request.values
    print(request_notify)
    RoomIDList = request_notify['RoomIDList']
    print(RoomIDList)
    notifyRes = Controller.notification(RoomIDList)
    notifyList = {'res':notifyRes}
    return json.dumps(notifyList, ensure_ascii=False)

# 檢舉功能
@app.route("/saveToken", methods=["POST"])
def report():
    request_report = request.values
    UserID = request_report['UserID']
    Token = request_report['Token']
    saveResult = Controller.saveUserToken(UserID,Token)
    return saveResult

@app.route("/keepLogin", methods=["POST"])
def keepLogin():
    request_keepLogin = request.values
    UserID = request_keepLogin['UserID']
    UUID = request_keepLogin['uuid']
    result = Controller.compareUUID(UserID,UUID)
    compareResult = {'res':result}
    return json.dumps(compareResult, ensure_ascii=False).encode('utf8')


if __name__ == "__main__":
    app.run(host=config['Server']['server_ip'],port='4002')
    # handler = logging.FileHandler('flask.log', encoding='UTF-8')
    # handler.setLevel(logging.DEBUG) 
    # logging_format = logging.Formatter(
    #     '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    # handler.setFormatter(logging_format)
    # app.logger.addHandler(handler)
    # app.run(ssl_context=('ceca.crt', 'private.key'),host=config['Server']['server_ip'],
    # port=config['Server']['portForRedis'],threaded=True)
    