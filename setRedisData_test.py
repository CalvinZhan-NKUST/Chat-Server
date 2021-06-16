import redis
import sys
import json
import Model5000 as Model
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_  
from sqlalchemy import text
import configparser


Session = Model.sessionmaker(bind=Model.DBLink)

r = redis.StrictRedis('localhost', encoding='utf-8', decode_responses=True)


def main():
    session = Session()
    MaxRoomID = session.query(Model.chatRoom).order_by(Model.chatRoom.RoomID.desc()).limit(1)
    minRoomID = session.query(Model.chatRoom).order_by(Model.chatRoom.RoomID).limit(1)
    # userList = session.query(Model.chatInfo)
    MaxRoomSN = 0
    minRoomSN = 0
    for i in MaxRoomID:
        print('MaxRoomID:'+str(i.RoomID))
        MaxRoomSN = int(i.RoomID)
    for n in minRoomID:
        print('minRoomID:'+str(n.RoomID))
        minRoomSN = int(n.RoomID)
    
    for m in range(minRoomSN,(MaxRoomSN+1),1):
        sql_cmd = 'select * from {roomID}msgList order by MsgID desc limit 10'.format(roomID = m)
        query_data = session.execute(sql_cmd)
        for i in query_data:
            msgID = str(i.MsgID)
            MsgMap={
                    'RoomID':i.RoomID,
                    'MsgID':i.MsgID,
                    'SendUserID':i.SendUserID,
                    'SendName':i.SendName,
                    'ReceiveName':i.ReceiveName,
                    'ReceiveUserID':i.ReceiveUserID,
                    'MsgType':i.MsgType,
                    'Text':i.Text,
                    'DateTime':i.DateTime   
                }
            jsonMap = json.dumps(MsgMap,ensure_ascii=False)
            print(m)
            print(jsonMap)
            print(msgID[-1])
            if msgID[-1]=='0':
                result = r.hget(m,10)
                if  str(result)=='None':
                    r.hmset(m,{'10':jsonMap})
            else:
                result = r.hget(m,msgID[-1])
                if  str(result)=='None':
                    r.hmset(m,{msgID[-1]:jsonMap})



    for k in range(minRoomSN,(MaxRoomSN+1),1):
        sql_cmd = 'select * from {roomID}msgList order by MsgID desc limit 1'.format(roomID = k)
        query = session.execute(sql_cmd)
        for i in query:
            r.set(str(k)+'MaxSN',i.MsgID)
            if (i.MsgID)<10:
                r.set(str(k)+'baseSN',1)
            else:
                r.set(str(k)+'baseSN',((i.MsgID)-10))

    

            

if __name__ == "__main__":
    main()
