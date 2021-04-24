# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, redirect
from datetime import datetime,timezone,timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_sso import SSO
from gevent import pywsgi
import configparser
import sys
import json
import Model5000 as Model
import Controller5000 as Controller
import Controller4000 as Controller4000

app = Flask(__name__)

db = SQLAlchemy()

config = configparser.ConfigParser()
config.read('config.ini')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config["DataBase"]["SQLALCHEMY_TRACK_MODIFICATIONS"]
app.config['SQLALCHEMY_DATABASE_URI'] = config["DataBase"]["SQLALCHEMY_DATABASE_URI"] + '?charset=utf8mb4'

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
@app.route('/createNewChatRoom', methods=["POST"])
def createNewChatRoom():
    request_roomID = request.values
    addUserID = request_roomID['UserID']
    UserIDList = request_roomID['UserIDList']
    RoomType = request_roomID['RoomType']
    RoomName = request_roomID['RoomName']
    
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    DateTime = str(dt2.strftime("%Y-%m-%d %H:%M:%S"))

    newRoomID = Controller.insertNewRoom(str(RoomType), RoomName)

    UserID = ''
    InsertUserCmd = ''

    for i in UserIDList:
        if i in ',':
            InsertUserCmd += '('+str(newRoomID)+','+str(UserID)+',\''+str(DateTime)+'\'),'
            UserID = ''
        else:
            UserID += i

    InsertUserCmd = InsertUserCmd[:-1]+';'
    result = db.engine.execute("INSERT INTO chatinfo (RoomID,UserID,JoinDateTime) VALUES "+InsertUserCmd)

    sql_cmd = """
    CREATE TABLE """ + newRoomID + """msgList (
    MsgID INT NOT NULL,
    RoomID INT NOT NULL,
    SendUserID INT NOT NULL,
    SendName VARCHAR(100) NOT NULL,
    ReceiveName VARCHAR(100) NOT NULL,
    ReceiveUserID INT NOT NULL,
    MsgType VARCHAR(100) NOT NULL,
    Text VARCHAR(100) NOT NULL,
    DateTime VARCHAR(100) NOT NULL,
    PRIMARY KEY (MsgID)
    )
    """
    print(sql_cmd)
    query_data = db.engine.execute(sql_cmd)
    res = Controller4000.updateRoomNum(UserIDList, RoomType, newRoomID, addUserID)
    print(res)
    return str(newRoomID)

@app.route("/getConfigPara", methods=["POST"])
def getConfigPara():
    request_config = request.values
    UserID = request_config['UserID']
    print('getMSgPara=ID'+UserID)
    responseConfig = {'MsgPara':config['MessageBalance']['messageNum']}
    return json.dumps(responseConfig, ensure_ascii=False)

@app.route("/getVersionCode", methods=["POST"])
def getVersionCode():
    versionCode = {'NowVersion':config['Server']['minVersionCode']}
    return json.dumps(versionCode, ensure_ascii=False)

@app.route("/getHistoryMsg", methods=["POST"])
def getHistoryMsg():
    msgHistory = []
    msgRes=''
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

@app.route("/searchUser", methods=["POST"])
def searchUser():
    request_searchUser = request.values
    Account = request_searchUser["searchValue"]
    UserID = request_searchUser["UserID"]
    searchResult = Controller.searchUser(Account, UserID)
    searchRes = {'res':searchResult}
    return json.dumps(searchRes, ensure_ascii=False)

@app.route("/updateUserName", methods=["POST"])
def updateUserName():
    request_update = request.values
    UserName = request_update['UserName']
    UserID = request_update['UserID']
    updateResult = Controller.updateUserInfo('UserName',UserID,UserName)
    return updateResult

@app.route("/uploadUserImage", methods=["POST"])
def uploadUserImage():
    request_updateImage = request.values
    ImageUrl = request_updateImage['UserImageUrl']
    UserID = request_updateImage['UserID']
    updateResult = Controller.updateUserInfo('UserImgURL',UserID,ImageUrl)
    return updateResult

@app.route("/updateUserPassword", methods=["POST"])
def updateUserPassword():
    request_password = request.values
    oldPassword = request_password['oldPassword']
    newPassword = request_password['newPassword']
    userID = request_password['UserID']
    updatePwdRes = Controller.updatePassword(oldPassword, newPassword, userID)
    return updatePwdRes

    

if __name__ == "__main__":
    # app.run(host=config['Server']['server_ip'],port=config['Server']['port'])
    portNumber = str(sys.argv[1])
    app.run(host=config['Server']['server_ip'],port=portNumber)
