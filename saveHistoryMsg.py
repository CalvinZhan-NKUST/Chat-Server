from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_  
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
import sys
import json
import Model5000 as Model
import Controller4000 as con
import configparser
import logging 

Session = Model.sessionmaker(bind=Model.DBLink)

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='SaveHisMsg.log', filemode='w', format=FORMAT)

db = SQLAlchemy()
app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config["DataBase"]["SQLALCHEMY_TRACK_MODIFICATIONS"]
app.config['SQLALCHEMY_DATABASE_URI'] = config["DataBase"]["SQLALCHEMY_DATABASE_URI"]+'?charset=utf8mb4'
db.init_app(app)


def saveHistoryMessage(MsgID, RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime):
    session = Session()
    try:

        #儲存訊息到同一張表單
        session.add(Model.msgInfo(RoomID=int(RoomID), RoomMsgSN=int(MsgID), SendUserID=int(SendUserID), SendName=str(SendName), ReceiveName=str(ReceiveName), ReceiveUserID=ReceiveUserID, MsgType=str(MsgType), Text=str(Text), DateTime=str(DateTime), Notify=1))

        #更新最新訊息的時間
        updateTime = session.query(Model.chatInfo).filter(Model.chatInfo.RoomID==int(RoomID)).update({'LastMsgTime':str(DateTime)})

        session.commit()
        session.close()
    except Exception as e: 
        logging.error("Catch an exception.", exc_info=True)
        print(e)
    return 'ok'

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    saveHistoryMessage(*sys.argv[1:])
