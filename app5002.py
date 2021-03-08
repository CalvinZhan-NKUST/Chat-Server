# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_sso import SSO
from gevent import pywsgi
import configparser
import json
import Model5000 as Model
import Controller5000 as Controller
app = Flask(__name__)

db = SQLAlchemy()

config = configparser.ConfigParser()
config.read('config.ini')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config["DataBase"]["SQLALCHEMY_TRACK_MODIFICATIONS"]
app.config['SQLALCHEMY_DATABASE_URI'] = config["DataBase"]["SQLALCHEMY_DATABASE_URI"]

db.init_app(app)

ext = SSO(app=app)


# 登入
@app.route("/login", methods=['POST']) 
def userLogin():
    request_login = request.values
    print(request_login)
    account = request_login['account']
    print(account)
    password = request_login['password']
    print(password)
    userLoginRes = Controller.userLogin(account, password)
    userInfo = {'res':userLoginRes}     
    return json.dumps(userInfo, ensure_ascii=False)

    

# 取得聊天室列表
@app.route('/getChatRoomList', methods=["POST"])
def getChatRoomList():
    request_roomList = request.values
    userName=request_roomList['UserName']
    userID=request_roomList['UserID']
    RoomListRes = Controller.getUserChatRoom(userName, userID)
    data = {'res':RoomListRes}
    return json.dumps(data, ensure_ascii=False)

# 創建新的聊天室 記得做防止SQL Injection
@app.route('/createSingleChatRoom', methods=["POST"])
def index():
    request_roomID = request.values
    UserID_A = request_roomID['UserID_A']
    UserID_B = request_roomID['UserID_B']

    newRoomID = Controller.insertSingleRoom(UserID_A,UserID_B)
    print(newRoomID)

    sql_cmd = """
    CREATE TABLE """ + newRoomID + """msgList (
    MsgID INT NOT NULL,
    RoomID INT NOT NULL,
    SendUserID INT NOT NULL,
    SendName VARCHAR(45) NOT NULL,
    ReceiveName VARCHAR(45) NOT NULL,
    ReceiveUserID INT NOT NULL,
    MsgType VARCHAR(45) NOT NULL,
    Text VARCHAR(45) NOT NULL,
    DateTime VARCHAR(45) NOT NULL,
    PRIMARY KEY (MsgID)
    )
    """
    print(sql_cmd)
    query_data = db.engine.execute(sql_cmd)
    print(query_data)
    return str(newRoomID)

# 送訊息 記得做防止SQL Injection
@app.route("/send", methods=["POST"]) 
def sendMsg():
    request_send = request.values
    MsgID = request_send['MsgID']
    RoomID = request_send['RoomID']
    SendUserID = request_send['SendUserID']
    MsgType = request_send['MsgType']
    SendName = request_send['SendName']
    ReceiveName = request_send['ReceiveName']
    ReceiveUserID = request_send['ReceiveUserID']
    Text = request_send['Text']
    DateTime = request_send['DateTime']

    sql_insert = """
    INSERT INTO  {RoomID_Table}msgList
    (MsgID, RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime) 
    VALUES({MsgID_insert}, {RoomID_insert}, {SendUserID_insert}, "'"{SendName_insert}"'", "'"{ReceiveName_insert}"'", 
    {ReceiveUserID_insert}, "'"{MsgType_insert}"'", "'"{Text_insert}"'", "'"{DateTime_insert}"'")
    """.format(RoomID_Table = RoomID, MsgID_insert = MsgID, RoomID_insert = RoomID, SendUserID_insert = SendUserID, 
    SendName_insert = SendName, ReceiveName_insert = ReceiveName, ReceiveUserID_insert = ReceiveUserID, MsgType_insert = MsgType,
    Text_insert = Text, DateTime_insert = DateTime)
    
    print(sql_insert)
    query_data = db.engine.execute(sql_insert)
    print(query_data)
    return 'ok'

@app.route("/getConfigPara", methods=["POST"])
def getConfigPara():
    request_config = request.values
    UserID = request_config['UserID']
    print('getMSgPara='+UserID)
    responseConfig = {'MsgPara':config['MessageBalance']['messageNum']}
    return json.dumps(responseConfig, ensure_ascii=False)

@app.route("/getVersionCode", methods=["POST"])
def getVersionCode():
    versionCode = {'NowVersion':config['Server']['versionCode']}
    return json.dumps(versionCode, ensure_ascii=False)

@app.route("/getHistoryMsg", methods=["POST"])
def getHistoryMsg():
    msgHistory = []
    request_getHsitoryMsg = request.values
    MsgID = request_getHsitoryMsg['MsgID']
    RoomID = request_getHsitoryMsg['RoomID']
    getMsgNum = config['MessageBalance']['messageNum']
    MsgEnd = int(MsgID)-int(getMsgNum)
    sql_cmd="""
    Select * from {RoomID}msgList 
    where MsgID between '{MsgEnd}' and '{MsgID}'
    order by MsgID
    """.format(RoomID = RoomID, MsgID = MsgID, MsgEnd = MsgEnd)
    print(sql_cmd)
    query_data = db.engine.execute(sql_cmd).fetchall()
    print(query_data)
    for i in query_data:
        Msg={
                'RoomID':i['RoomID'],
                'MsgID':i['MsgID'],
                'SendUserID':i['SendUserID'],
                'SendName':i['SendName'],
                'ReceiveName':i['ReceiveName'],
                'ReceiveUserID':i['ReceiveUserID'],
                'MsgType':i['MsgType'],
                'Text':i['Text'],
                'DateTime':i['DateTime']   
            }
        msgHistory.append(Msg)
        msgRes = {'res':msgHistory}
        
    return json.dumps(msgRes, ensure_ascii=False)

@app.route("/register", methods=["POST"])
def register():
    request_register = request.values
    Account = request_register['account']
    Password = request_register['password']
    Name = request_register['name']
    registerResult = Controller.registerNewUser(Account, Password, Name)
    registerRes = {'res':registerResult}
    return json.dumps(registerRes, ensure_ascii=False)

    
if __name__ == "__main__":
    # app.run(host=config['Server']['server_ip'],port=config['Server']['port'])
    app.run(host=config['Server']['server_ip'],port='5002')