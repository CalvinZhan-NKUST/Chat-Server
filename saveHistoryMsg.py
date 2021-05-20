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

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='flask.log', filemode='w', format=FORMAT)

Session = Model.sessionmaker(bind=Model.DBLink)

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
        #儲存訊息到單一表單
        sql_insert = "INSERT INTO {RoomID_Table}msgList(MsgID, RoomID, SendUserID, SendName, ReceiveName, ReceiveUserID, MsgType, Text, DateTime) VALUES({MsgID_insert}, {RoomID_insert}, {SendUserID_insert}, \'{SendName_insert}\', \'{ReceiveName_insert}\', {ReceiveUserID_insert}, \'{MsgType_insert}\', \'{Text_insert}\', \'{DateTime_insert}\')".format(RoomID_Table = RoomID, MsgID_insert = MsgID, RoomID_insert = RoomID, SendUserID_insert = SendUserID, SendName_insert = SendName, ReceiveName_insert = ReceiveName, ReceiveUserID_insert = ReceiveUserID, MsgType_insert = MsgType,Text_insert = str(Text), DateTime_insert = DateTime)
        # query_data = db.engine.execute(sql_insert)
        session.execute(sql_insert)

        #儲存訊息到同一張表單
        session.add(Model.msgInfo(RoomID=int(RoomID), RoomMsgSN=int(MsgID), SendUserID=int(SendUserID), SendName=str(SendName), ReceiveName=str(ReceiveName), ReceiveUserID=ReceiveUserID, MsgType=str(MsgType), Text=str(Text), DateTime=str(DateTime), Notify=1))
        session.commit()
        session.close()
    except Exception as e: 
        logging.error("Catch an exception.", exc_info=True)
        print(e)
    return 'ok'

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    saveHistoryMessage(*sys.argv[1:])
