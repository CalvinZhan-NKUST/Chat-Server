from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_  
from sqlalchemy import text
from datetime import datetime,timezone,timedelta
import Model5000 as Model
import Controller4000 as Model4003
import bcrypt
import json
import uuid

Session = Model.sessionmaker(bind=Model.DBLink)

if __name__ == "__main__":
    session = Session()

    userInfoList = session.query(Model.userInfo)
    for i in userInfoList:
        print(i.Account)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw((i.Password).encode('utf8'), salt)
        updateRes = session.query(Model.userInfo).filter(Model.userInfo.UserID==int(i.UserID)).update({'Password':str(hashed.decode('utf8'))})
        session.commit()

    newUserInfoList = session.query(Model.userInfo)
    for n in newUserInfoList:
        print(n.UserID)
        print(n.Password+'\n')

    session.close()