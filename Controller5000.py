from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_  
from sqlalchemy import text
from datetime import datetime,timezone,timedelta
import Model5000 as Model
import bcrypt
import json
import uuid
import asyncio
import time

Session = Model.sessionmaker(bind=Model.DBLink)


# 使用者取得自己的聊天室清單
# UserID = 2, UserName = 朱彥銘
def getUserChatRoom(user, userID):
    session = Session()
    RoomList=[]
    resRoomList=[]
    resRoom={}
    send=''
    Name=''
    roomGet=''
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
        sendSQL = '(' + send[:-4] + ')' + ' and user_chatroom.UserName !=' + '\'' + user +'\''
        userChatRoomList = session.query(Model.user_chatroom).filter((text(sendSQL)))
        for m in userChatRoomList:
            print(m.UserName)
            print(m.RoomID)
            Name=(m.UserName).encode('utf-8').decode()
            resRoom={'UserName':Name, 'RoomID':m.RoomID, 'UserID':m.UserID, 'UserImageUrl':m.UserImgUrl, 'LastMsgTime':m.LastMsgTime}
            resRoomList.append(resRoom)
    else:
        print('沒有單人聊天室')
    # 取得群組
    groupList = session.query(Model.user_chatroom).filter(Model.user_chatroom.RoomType=='2',Model.user_chatroom.UserID==userID)
    for n in groupList:
        print(n.RoomID)
        groupName=session.query(Model.grouproom).filter(Model.grouproom.RoomID==n.RoomID)
        for k in groupName:    
            resRoom={'UserName':k.GroupName, 'RoomID':str(k.RoomID), 'UserID':'0', 'UserImageUrl':k.ImageURL,  'LastMsgTime':n.LastMsgTime}
            resRoomList.append(resRoom)
    session.close()
    return resRoomList

# 使用者取得自己的聊天室清單
def getUserChatRoomLimit(user, userID, roomNumStart, getRoomQuantity):
    session = Session()
    RoomList=[]
    resRoomList=[]
    resRoom={}
    send=''
    Name=''
    roomGet=''

    # 取得RoomID列表
    sql_query = 'select * from user_chatroom where UserName=\'{userName}\' order by LastMsgTime desc limit {getRoomNum},{getRoomLocate};'.format(userName=str(user),getRoomNum=int(roomNumStart),getRoomLocate=int(getRoomQuantity))
    # roomIDList = session.query(Model.user_chatroom).filter(Model.user_chatroom.UserName==user).order_by(Model.user_chatroom.LastMsgTime.desc).limit(roomNumStart).offset(int(getRoomQuantity)).all()
    roomIDList = session.execute(sql_query)
    for i in roomIDList:
        print(i.UserName)
        print(i.RoomID)
        roomGet=i.RoomID
        RoomList.append('user_chatroom.RoomID=\'' + str(i.RoomID) + '\'') 

    if roomGet!='':
        for j in range(len(RoomList)):
            send += RoomList[j] + " or "
        sendSQL = '(' + send[:-4] + ')' + ' and user_chatroom.UserName !=' + '\'' + user +'\' order by LastMsgTime desc'
        userChatRoomList = session.query(Model.user_chatroom).filter((text(sendSQL)))
        for m in userChatRoomList:
            if str(m.RoomType)=='1':
                resRoom={'UserName':m.UserName, 'RoomID':m.RoomID, 'UserID':m.UserID, 'UserImageUrl':m.UserImgUrl, 'LastMsgTime':m.LastMsgTime}
                resRoomList.append(resRoom)
            else:
                groupList = session.query(Model.grouproom).filter(Model.grouproom.RoomID==int(m.RoomID))
                for n in groupList:
                    print(n.RoomID)
                    resRoom={'UserName':n.GroupName, 'RoomID':str(n.RoomID), 'UserID':'0', 'UserImageUrl':n.ImageURL, 'LastMsgTime':m.LastMsgTime}
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
        session = Session()
        UserUUID = ''
        userInfo = session.query(Model.userInfo).filter(Model.userInfo.Account==account)
        for i in userInfo:
            UserID = i.UserID
            UserName = i.UserName
            UserImgURL = i.UserImgURL
            userPwd = i.Password

        if (bcrypt.checkpw(password.encode('utf8'), userPwd.encode('utf8'))):
            setbcryptID='UserID_'+str(UserID)
            salt = bcrypt.gensalt(rounds=10)
            userToken = bcrypt.hashpw(setbcryptID.encode('utf8'), salt)
            tokenTimeStamp = int(round(time.time()*1000))
            UserUUID = str(userToken.decode('utf8'))+str(tokenTimeStamp)
            
            print(userPwd)
            userInformation = {'UserID':UserID, 'UserName':UserName, 'UserImgURL':UserImgURL, 'uuid':UserUUID}
            userInfoList.append(userInformation)
            session.close()
            return userInfoList
        else:
            session.close()
            resLog='登入失敗'
            return resLog

#新增聊天室
def insertNewRoom(RoomType, RoomName, UserIDList, DateTime):
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    DateTime = str(dt2.strftime("%Y-%m-%d %H:%M:%S"))

    session = Session()
    result = session.query(Model.chatRoom).order_by(Model.chatRoom.RoomID.desc()).limit(1)
    for i in result:
        MaxRoomSN = i.RoomID

    NewRoomID = int(MaxRoomSN) + 1

    if RoomType == '1':
        session.add(Model.chatRoom(RoomID=NewRoomID,RoomType=1, RoomLocate='none'))
    elif RoomType == '2':
        session.add(Model.chatRoom(RoomID=NewRoomID,RoomType=2, RoomLocate='none'))
        session.add(Model.grouproom(GroupName=RoomName, RoomID=NewRoomID, ImageURL='none'))
    session.commit()

    UserID=''
    for i in UserIDList:
        if i in ',':
            session.add(Model.chatInfo(RoomID=NewRoomID,UserID=UserID,JoinDateTime=DateTime,LastMsgTime=DateTime))
            session.commit()
            UserID = ''
        else:
            UserID += i
    
    session.close()
    return str(NewRoomID)   

# 更新聊天室勿這
def updateRoomLocate(RoomID, Locate):
    session = Session()
    chatLocateUpdate = session.query(Model.chatroom).filter(Model.chatroom.RoomID==int(RoomID)).update({'RoomLocate':str(Locate)})
    session.commit()
    session.close()
    return 'ok'

# 加入新的使用者到聊天室中
def addNewUserToGroupRoom(RoomID,UserID,DateTime):
    session = Session()

    searchUser = session.query(Model.chatInfo).filter(Model.chatInfo.RoomID==RoomID,Model.chatInfo.UserID==UserID).count()
    print("人數："+str(searchUser))
    if(searchUser!=0):
        return '使用者已在聊天室中'
    else:
        session.add(Model.chatInfo(RoomID=RoomID,UserID=UserID,JoinDateTime=DateTime,LastMsgTime=DateTime))
        chatUpdate = session.query(Model.chatInfo).filter(Model.chatInfo.RoomID==int(RoomID)).update({'LastMsgTime':str(DateTime)})
        session.commit()
        session.close()
        return 'ok'

# 搜尋聊天室使用者
def searchUserInGroup(RoomID):
    resUserID=[]
    UserIDInfo={}
    session = Session()

    # sql_query = 'select * from user_chatroom where RoomID='+str(RoomID)+';'
    # searchGroupUserResult = session.execute(sql_query)

    searchGroupUserResult = session.query(Model.user_chatroom).filter(Model.user_chatroom.RoomID==int(RoomID))

    for i in searchGroupUserResult:
        print(i.UserID+' , '+i.RoomID)
        UserIDInfo = {'UserID':i.UserID,'UserName':i.UserName}
        resUserID.append(UserIDInfo)

    session.close()
    return resUserID

# 將使用者踢出聊天室
def kickUserOutOfGroup(RoomID,UserID):
    session = Session()
    session.query(Model.chatInfo).filter(Model.chatInfo.RoomID==int(RoomID),Model.chatInfo.UserID==int(UserID)).delete()
    session.commit()
    session.close()
    return 'ok'

# 註冊新的使用者
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

#檢查Token是否有被修改
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
            return 'denied'

        checkToken = Token.split(str(tokenTime),1)
        compareUser = 'UserID_'+str(UserID)
        if bcrypt.checkpw(compareUser.encode('utf8'),checkToken[0].encode('utf8')):
            return 'pass'
        else:
            return 'denied'
    except:
        return 'denied'


def get_formattime_from_timestamp(time_stamp):
    format_pattern = "%Y-%m-%d %H:%M:%S"
    date_array = datetime.fromtimestamp(time_stamp)
    time_str = date_array.strftime(format_pattern)
    return time_str
