# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, UniqueConstraint, Index # 元素/主key
from sqlalchemy import Integer, String, VARCHAR, TEXT, DATE
from sqlalchemy.orm import sessionmaker, relationship, backref # 創接口/建立關系relationship(table.ID)
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool# sqlalchemy 查詢前連結，结束後，調用 session.close() 關閉連結
from sqlalchemy import desc,asc #降序
import configparser
import json


config = configparser.ConfigParser()
config.read('config.ini')
user = config["DataBase"]["User"]
password = config["DataBase"]["Password"]
host = config["DataBase"]["Host"]
DB_name = config["DataBase"]["DB_Name"]
DBInfo = "mysql+pymysql://"+ user +":"+password+ "@" + host+ "/" + DB_name+"?charset=utf8mb4"

DBLink = create_engine(DBInfo, poolclass=NullPool)# 創建一個空的資料庫
Base = declarative_base()# 創數據結構放資料

# 使用者加入聊天室的資料表
class chatInfo(Base):
    __tablename__='chatinfo'
    ChatID = Column(Integer, primary_key=True)
    RoomID = Column(Integer, nullable=False)
    UserID = Column(Integer, nullable=False)
    JoinDateTime = Column(VARCHAR(45), nullable=False)

    def __init__(self, RoomID, UserID, JoinDateTime):
        self.RoomID = RoomID
        self.UserID = UserID
        self.JoinDateTime = JoinDateTime
        
# 聊天室數量與列表
class chatRoom(Base):
    __tablename__ = 'chatroom'
    RoomID = Column(Integer, primary_key=True)
    RoomType = Column(Integer, nullable=False)

    def __init__(self, RoomID, RoomType):
        self.RoomID = RoomID
        self.RoomType = RoomType

# 多人群組列表
class grouproom(Base):
    __tablename__ = 'grouproom'
    GroupRoomID = Column(Integer, primary_key=True)
    RoomID = Column(Integer, nullable=False)
    GroupName = Column(VARCHAR(45), nullable=False)
    ImageURL = Column(VARCHAR(45),nullable=False)

    def __init__(self, RoomID, GroupName, ImageURL):
        self.RoomID = RoomID
        self.GroupName = GroupName
        self.ImageURL = ImageURL

# 伺服器列表
class serverList(Base):
    __tablename__ = 'serverlist'
    ServerID = Column(Integer, primary_key=True)
    ServerIP = Column(VARCHAR(45), nullable=False)

    def __init__(self, ServerID, ServerIP):
        self.ServerIP = ServerIP


# 使用者資訊列表
class userInfo(Base):
    __tablename__ = 'userinfo'
    UserID = Column(Integer, primary_key=True)
    Account = Column(VARCHAR(45), nullable=False)
    Password = Column(VARCHAR(45), nullable=False)
    UserName = Column(VARCHAR(45), nullable=False)
    UserImgURL = Column(VARCHAR(45), nullable=True)

    def __init__(self, Account, Password, UserName, UserImgURL):
        self.Account = Account
        self.Password = Password
        self.UserName = UserName
        self.UserImgURL = UserImgURL


# 單一則訊息資訊與列表
class msgInfo(Base):
    __tablename__ = 'msginfo'
    MsgID = Column(Integer, primary_key=True)
    RoomID = Column(Integer, nullable=False)
    SendUserID = Column(Integer, nullable=False)
    SendName = Column(VARCHAR(45),nullable=False)
    ReceiveName = Column(VARCHAR(45),nullable=False)
    ReceiveUserID = Column(VARCHAR(45),nullable=False)
    MsgType = Column(String, nullable=False)
    Text = Column(String, nullable=False)
    DateTime = Column(VARCHAR(45), nullable=False)
    Notify = Column(VARCHAR(45), nullable=False)
    def __init__(self, RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime, Notify):
        self.RoomID = RoomID
        self.SendUserID = SendUserID
        self.SendName = SendName
        self.ReceiveName = ReceiveName
        self.ReceiveUserID = ReceiveUserID
        self.MsgType = MsgType
        self.Text = Text
        self.DateTime = DateTime
        self.Notify = Notify

# 這是一張View；每位使用者待在哪些聊天室中
class user_chatroom(Base):
    __tablename__ = 'user_chatroom'
    RoomID = Column(Integer, nullable=False,primary_key=True)
    UserID = Column(Integer,nullable=False)
    UserName = Column(VARCHAR(45),nullable=False)
    ImageURL = Column(VARCHAR(45),nullable=False)
    RoomType = Column(Integer,nullable=False)

    def __init__(self, RoomID, UserID, UserName, ImageURL, RoomType):
        self.RoomID = RoomID
        self.UserID = UserID
        self.UserName = UserName
        self.ImageURL = ImageURL
        self.RoomType = RoomType


def init_db():
    Base.metadata.create_all(DBLink)

def drop_db():
    Base.metadata.drop_all(DBLink)
