from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_  
from sqlalchemy import text
import Model5000 as Model
import json

RoomID=223
MsgID=50
getMsgNum=5
EndNum=MsgID-getMsgNum

Session = Model.sessionmaker(bind=Model.DBLink)

session = Session()
sql_cmd="""
Select * from """ + RoomID+"""msgList 
where MsgID between'"""+MsgID+"""' and '"""+EndNum+"""'
 order by MsgID
"""
query_data = db.engine.execute(sql_cmd)
print(query_data)