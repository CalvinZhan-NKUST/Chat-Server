# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, session, redirect
from datetime import datetime,timezone,timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_sso import SSO
from gevent import pywsgi
import Model5000 as Model
import Controller5000 as Controller
import Controller4000 as Controller4000
import configparser
import sys
import json

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
    token = request_roomList['Token']

    compareRes = Controller.compareToken(userID,token)
    if str(compareRes) == 'pass':
        RoomListRes = Controller.getUserChatRoom(userName, userID)
        data = {'res':RoomListRes}
    else:
        data = {'res':'Token驗證失敗'}

    return json.dumps(data, ensure_ascii=False)

# 分批取得聊天室列表
@app.route('/getChatRoomListLimit', methods=["POST"])
def getChatRoomListLimit():
    request_roomList = request.values
    userName=request_roomList['UserName']
    userID=request_roomList['UserID']
    token = request_roomList['Token']
    roomNumStart=request_roomList['roomNumStart']
    getRoomQuantity=request_roomList['getRoomQuantity']

    compareRes = Controller.compareToken(userID,token)
    if str(compareRes) == 'pass':
        RoomListRes = Controller.getUserChatRoomLimit(userName, userID, roomNumStart, getRoomQuantity)
        data = {'res':RoomListRes}
    else:
        data = {'res':'Token驗證失敗'}
    return json.dumps(data, ensure_ascii=False)

# 創建新的聊天室 記得做防止SQL Injection
@app.route('/createNewChatRoom', methods=["POST"])
def createNewChatRoom():
    request_roomID = request.values
    addUserID = request_roomID['UserID']
    Token = request_roomID['Token']
    UserIDList = request_roomID['UserIDList']
    RoomType = request_roomID['RoomType']
    RoomName = request_roomID['RoomName']
    
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    DateTime = str(dt2.strftime("%Y-%m-%d %H:%M:%S"))

    compareRes = Controller.compareToken(addUserID,Token)
    if str(compareRes) == 'pass':
        newRoomID = Controller.insertNewRoom(str(RoomType), RoomName)
        UserID = ''
        InsertUserCmd = ''
        for i in UserIDList:
            if i in ',':
                InsertUserCmd += '('+str(newRoomID)+','+str(UserID)+',\''+str(DateTime)+'\',\''+str(DateTime)+'\'),'
                UserID = ''
            else:
                UserID += i

        InsertUserCmd = InsertUserCmd[:-1]+';'
        result = db.engine.execute("INSERT INTO chatinfo (RoomID,UserID,JoinDateTime,LastMsgTime) VALUES "+InsertUserCmd)
        sql_cmd = """
        CREATE TABLE """ + newRoomID + """msgList (
        MsgID INT NOT NULL,
        RoomID INT NOT NULL,
        SendUserID INT NOT NULL,
        SendName VARCHAR(100) NOT NULL,
        ReceiveName VARCHAR(100) NOT NULL,
        ReceiveUserID INT NOT NULL,
        MsgType VARCHAR(100) NOT NULL,
        Text LONGTEXT NOT NULL,
        DateTime VARCHAR(100) NOT NULL,
        PRIMARY KEY (MsgID)
        )
        """
        print(sql_cmd)
        query_data = db.engine.execute(sql_cmd)
        res = Controller4000.updateRoomNum(UserIDList, RoomType, newRoomID, addUserID)
        print(res)
        resNewRoomID = {'RoomID':newRoomID, 'LastMsgTime':DateTime}
        return json.dumps(resNewRoomID, ensure_ascii=False)
    else:
        return 'Token驗證失敗'

# 新增使用者至群組中
@app.route("/addNewUserToGroup", methods=["POST"])
def addNewUserToGroup():
    request_addNewUser = request.values
    UserID = request_addNewUser['UserID']
    Token = request_addNewUser['Token']
    RoomID = request_addNewUser['RoomID']
    AddUserID = request_addNewUser['AddUserID']
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    DateTime = str(dt2.strftime("%Y-%m-%d %H:%M:%S"))
    print(str(request_addNewUser))
    compareRes = Controller.compareToken(UserID,str(Token))
    if str(compareRes) == 'pass':
        addRes = Controller.addNewUserToGroupRoom(RoomID, AddUserID, DateTime)
        return 'ok'
    else:
        return 'Token驗證失敗'

# 查詢聊天室內部成員
@app.route("/searchUserInGroup",methods=["POST"])
def searchUserInGroup():
    request_searchUserInGroup = request.values
    UserID = request_searchUserInGroup['UserID']
    Token = request_searchUserInGroup['Token']
    RoomID = request_searchUserInGroup['RoomID']
    compareRes = Controller.compareToken(UserID,str(Token))
    if str(compareRes) == 'pass':
        searchRes = Controller.searchUserInGroup(RoomID)
        return json.dumps(searchRes, ensure_ascii=False)
    else:
        return 'Token驗證失敗'
    

# 將使用者踢出群組
@app.route("/kickUser",methods=["POST"])
def kickUser():
    request_kickUser = request.values
    UserID = request_kickUser['UserID']
    Token = request_kickUser['Token']
    RoomID = request_kickUser['RoomID']
    KickUserID = request_kickUser['KickUserID']

    compareRes = Controller.compareToken(UserID,str(Token))
    if str(compareRes) == 'pass':
        kickResult = Controller.kickUserOutOfGroup(RoomID,KickUserID)
        kickRes = Controller4000.resetRoomMember(RoomID)
        return json.dumps(kickResult, ensure_ascii=False)
    else:
        return 'Token驗證失敗'


# 取得系統訊息取得參數
@app.route("/getConfigPara", methods=["POST"])
def getConfigPara():
    request_config = request.values
    UserID = request_config['UserID']
    Token = request_config['Token']
    
    compareRes = Controller.compareToken(UserID,Token)
    if str(compareRes) == 'pass':
        print('getMSgPara=ID'+UserID)
        responseConfig = {'MsgPara':config['MessageBalance']['messageNum']}
        return json.dumps(responseConfig, ensure_ascii=False)
    else:
        return 'Token驗證錯誤'

# 取得版本號
@app.route("/getVersionCode", methods=["POST"])
def getVersionCode():
    versionCode = {'NowVersion':config['Server']['minVersionCode']}
    return json.dumps(versionCode, ensure_ascii=False)

# 取得聊天室歷史訊息
@app.route("/getHistoryMsg", methods=["POST"])
def getHistoryMsg():
    msgHistory = []
    msgRes=''
    request_getHsitoryMsg = request.values
    Token = request_getHsitoryMsg['Token']
    UserID = request_getHsitoryMsg['UserID']
    MsgID = request_getHsitoryMsg['MsgID']
    RoomID = request_getHsitoryMsg['RoomID']
    getMsgNum = config['MessageBalance']['messageNum']

    compareRes = Controller.compareToken(UserID,Token)
    if str(compareRes) == 'pass':
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
    else:
        return 'Token驗證失敗'

# 註冊使用者
@app.route("/register", methods=["POST"])
def register():
    request_register = request.values
    Account = request_register['account']
    Password = request_register['password']
    Name = request_register['name']
    registerResult = Controller.registerNewUser(Account, Password, Name)
    registerRes = {'res':registerResult}
    return json.dumps(registerRes, ensure_ascii=False)

# 搜尋使用者
@app.route("/searchUser", methods=["POST"])
def searchUser():
    request_searchUser = request.values
    Account = request_searchUser["searchValue"]
    UserID = request_searchUser["UserID"]
    Token = request_searchUser["Token"]
    compareRes = Controller.compareToken(UserID,Token)
    if str(compareRes) == 'pass':
        searchResult = Controller.searchUser(Account, UserID)
        searchRes = {'res':searchResult}
        return json.dumps(searchRes, ensure_ascii=False)
    else:
        return 'Token驗證失敗'

# 更新使用者名稱
@app.route("/updateUserName", methods=["POST"])
def updateUserName():
    request_update = request.values
    UserName = request_update['UserName']
    UserID = request_update['UserID']
    Token = request_update['Token']
    compareRes = Controller.compareToken(UserID,Token)
    if str(compareRes) == 'pass':
        updateResult = Controller.updateUserInfo('UserName',UserID,UserName)
        return updateResult
    else:
        return 'Token驗證失敗'

# 更新使用者大頭照
@app.route("/uploadUserImage", methods=["POST"])
def uploadUserImage():
    request_updateImage = request.values
    ImageUrl = request_updateImage['UserImageUrl']
    UserID = request_updateImage['UserID']
    Token = request_updateImage['Token']
    compareRes = Controller.compareToken(UserID,Token)
    if str(compareRes) == 'pass':
        updateResult = Controller.updateUserInfo('UserImgURL',UserID,ImageUrl)
        return updateResult
    else:
        return 'Token驗證失敗'

# 更新使用者密碼
@app.route("/updateUserPassword", methods=["POST"])
def updateUserPassword():
    request_password = request.values
    oldPassword = request_password['oldPassword']
    newPassword = request_password['newPassword']
    userID = request_password['UserID']
    token = request_password['Token']
    compareRes = Controller.compareToken(userID,token)
    if str(compareRes) == 'pass':
        updatePwdRes = Controller.updatePassword(oldPassword, newPassword, userID)
        return updatePwdRes
    else:
        return 'Token驗證失敗'
    

if __name__ == "__main__":
    # app.run(host=config['Server']['server_ip'],port=config['Server']['port'])
    portNumber = str(sys.argv[1])
    app.run(host=config['Server']['server_ip'],port=portNumber,threaded=True)
