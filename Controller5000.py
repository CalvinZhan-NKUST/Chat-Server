from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_  
from sqlalchemy import text
from datetime import datetime,timezone,timedelta
import Model5000 as Model
import Controller4000 as Controller4000
import bcrypt
import json
import uuid
import asyncio
import time

Session = Model.sessionmaker(bind=Model.DBLink)
bracketsUp = '('
bracketsDown = ')'


# 測試Code
def select():
    session = Session()
    result = session.query(Model.userInfo).filter(or_(Model.userInfo.UserName=='朱彥銘',Model.userInfo.UserName=='YoChi')).all()
    for i in result:
        print(i.UserName) 
    session.close()
    return 'ok'

# 使用者取得自己的聊天室清單
def getUserChatRoom(user, userID):
    session = Session()
    RoomList=[]
    resRoomList=[]
    resRoom={}
    send=''
    Name=''
    roomGet=''
    global bracketsUp
    global bracketsDown
    # 取得RoomID列表
    roomIDList = session.query(Model.user_chatroom).filter(Model.user_chatroom.UserName==user,Model.user_chatroom.RoomType=='1')
    for i in roomIDList:
        print(i.UserName)
        print(i.RoomID)
        roomGet=i.RoomID
        RoomList.append('user_chatroom.RoomID=\'' + str(i.RoomID) + '\'') 
    session.close()
    # 取得聊天室除了自己之外的人名列表(單人聊天室)
    if roomGet!='':
        session = Session()
        for j in range(len(RoomList)):
            send += RoomList[j] + " or "
        sendSQL = bracketsUp + send[:-4] + bracketsDown + ' and user_chatroom.UserName !=' + '\'' + user +'\''
        userChatRoomList = session.query(Model.user_chatroom).filter((text(sendSQL)))
        for m in userChatRoomList:
            print(m.UserName)
            print(m.RoomID)
            Name=(m.UserName).encode('utf-8').decode()
            resRoom={'UserName':Name, 'RoomID':m.RoomID, 'UserID':m.UserID, 'UserImageUrl':m.ImageURL}
            resRoomList.append(resRoom)
    else:
        print('沒有單人聊天室')
    # 取得群組
    groupList = session.query(Model.user_chatroom).filter(Model.user_chatroom.RoomType=='2',Model.user_chatroom.UserID==userID)
    for n in groupList:
        print(n.RoomID)
        groupName=session.query(Model.grouproom).filter(Model.grouproom.RoomID==n.RoomID)
        for k in groupName:    
            resRoom={'UserName':k.GroupName, 'RoomID':str(k.RoomID), 'UserID':'0', 'UserImageUrl':k.ImageURL}
            resRoomList.append(resRoom)
    session.close()
    return resRoomList

# 使用者登入
def userLogin(account, password):
    session = Session()
    userInformation={}
    userInfoList=[]

    userLoginResult = session.query(Model.userInfo).filter(Model.userInfo.Account==account).count()
    print(userLoginResult)
    if(userLoginResult!=1):
        resLog='登入失敗'
        return resLog
    else:
        setUUID = uuid.uuid1()
        session = Session()
        userInfo = session.query(Model.userInfo).filter(Model.userInfo.Account==account)
        for i in userInfo:
            UserID = i.UserID
            UserName = i.UserName
            UserImgURL = i.UserImgURL
            userPwd = i.Password
            print(userPwd)
            userInformation = {'UserID':UserID, 'UserName':UserName, 'UserImgURL':UserImgURL, 'uuid':str(setUUID)}
            userInfoList.append(userInformation)
            Controller4000.setUUID(str(UserID),str(setUUID))

        if (bcrypt.checkpw(password.encode('utf8'), userPwd.encode('utf8'))):
            session.close()
            return userInfoList
        else:
            session.close()
            resLog='登入失敗'
            return resLog

#新增聊天室
def insertNewRoom(RoomType, RoomName):
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    DateTime = str(dt2.strftime("%Y-%m-%d %H:%M:%S"))

    session = Session()
    result = session.query(Model.chatRoom).order_by(Model.chatRoom.RoomID.desc()).limit(1)
    for i in result:
        MaxRoomSN = i.RoomID

    NewRoomID = int(MaxRoomSN) + 1

    if RoomType == '1':
        session.add(Model.chatRoom(RoomID=NewRoomID,RoomType=1))
    elif RoomType == '2':
        session.add(Model.chatRoom(RoomID=NewRoomID,RoomType=2))
        session.add(Model.grouproom(GroupName=RoomName, RoomID=NewRoomID, ImageURL='none'))

    session.commit()
    session.close()
    return str(NewRoomID)   

#註冊新的使用者
def registerNewUser(Account, Password, Name):
    session = Session()
    newUser = session.query(Model.userInfo).filter(Model.userInfo.Account==Account).count()
    if (newUser>0):
        session.close()
        return 'failure'
    else:
        salt = bcrypt.gensalt()
        passwordAdd = bcrypt.hashpw(Password.encode('utf8'), salt)
        print(passwordAdd)
        session.add(Model.userInfo(Account=Account,Password=str(passwordAdd.decode('utf8')),UserName=Name,UserImgURL='none'))
        session.commit()
        session.close()
        return 'success'

#尋找使用者
def searchUser(Account, UserID):
    session = Session()
    userSearchResult=[]
    searchResult = session.query(Model.userInfo).filter((Model.userInfo.Account.like('%'+Account+'%') | Model.userInfo.UserName.like('%'+Account+'%')), Model.userInfo.UserID!=UserID)
    print(Account)
    for i in searchResult:
        UserID = i.UserID
        UserName = i.UserName
        Account = i.Account
        UserImgURL = i.UserImgURL
        UserSearch = {'UserID':UserID, 'UserName':UserName, 'Account':Account, 'UserImgURL':UserImgURL}
        userSearchResult.append(UserSearch)
    session.close()
    return userSearchResult

#更新使用者資訊
def updateUserInfo(updateType, userID, updateInfo):
    session = Session()
    if (updateType=='UserName'):
        userUpdate = session.query(Model.userInfo).filter(Model.userInfo.UserID==int(userID)).update({'UserName':str(updateInfo)})
        session.commit()
        session.close()
        return 'ok'
    elif (updateType=='UserImgURL'):
        userUpdate = session.query(Model.userInfo).filter(Model.userInfo.UserID==int(userID)).update({'UserImgURL':str(updateInfo)})
        session.commit()
        session.close()
        return 'ok'
    else:
        session.close()
        return 'wrong update type !'

#更新使用者密碼
def updatePassword(oldPassword, newPassword, userID):
    session = Session()
    userPassword = session.query(Model.userInfo).filter(Model.userInfo.UserID==int(userID))
    passworded = ''
    for i in userPassword:
        passworded = i.Password
    if bcrypt.checkpw(oldPassword.encode('utf8'),passworded.encode('utf8')):
        print('密碼符合')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(newPassword.encode('utf8'), salt)
        pwdUpdate = session.query(Model.userInfo).filter(Model.userInfo.UserID==int(userID)).update({'Password':str(hashed.decode('utf8'))})
        session.commit()
        session.close()
        return 'Change success!'
    else:
        session.close()
        return 'Wrong password!'