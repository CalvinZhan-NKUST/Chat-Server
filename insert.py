from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_  
from sqlalchemy import text
import Model5000 as Model
import json

Session = Model.sessionmaker(bind=Model.DBLink)
def main():
    session = Session()

    # UserAdd = Model.chatRoom(
    #     Account='F108118121',
    #     Password='F108118121',
    #     UserName='詹祐祈',
    #     UserImgURL='none'
    # )
    # session.add_all([
    #         Student(ID=uuid.uuid4(), Name='Student1', School='School1', Sex='男生'),
    #         Student(ID=uuid.uuid4(), Name='Student2', School='School2', Sex='女生'),
    #         Student(ID=uuid.uuid4(), Name='Student3', School='School3', Sex='女生')])

    session.add_all([
        Model.chatInfo(RoomID='223', UserID='1' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='2' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='3' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='4' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='5' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='6' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='7' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='8' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='9' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='10' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='11' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='12' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='13' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='14' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='15' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='16' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='17' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='18' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='19' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='20' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='21' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='22' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='23' , JoinDateTime='20201218'),
        Model.chatInfo(RoomID='223', UserID='24' , JoinDateTime='20201218'),
    ])

    # session.add_all([
    #     Model.chatRoom(RoomID=223)
    # ])
    
    # roomAdd = Model.chatRoom(RoomID=223)
    # session.add(roomAdd)
    session.commit()
    session.close()



if __name__=='__main__':
    main()