import subprocess
import time
import threading

def tryNotify(xyz):

    print(xyz)
    localtime = time.asctime( time.localtime(time.time()) )
    print(localtime)
    n = 0

    for i in range(200):
        i="1"
        RoomID="100"
        Topic = 'User_'+i+"/"+RoomID
        MsgID=60
        SendName="詹祐祈"
        Text="台灣有座阿里山"
        notifiType='Message'
        SendUserID='3'
        msgType='Text'
        # Topic, RoomID, MsgID, SendName, Text, NotifiType, userID, msgType
        # mqttPush.sendNotify(Topic,RoomID,MsgID,SendName,Text)
        command = "python3 mqttNotification.py " +str(Topic)+" "+str(RoomID)+" "+str(MsgID)+" "+str(SendName)+" "+str(Text)+" "+notifiType+" "+SendUserID+" "+msgType
        subprocess.Popen(command, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")

    localtime2 = time.asctime( time.localtime(time.time()) )
    print(localtime2)


def startTesting():
    print('開始')
    t = threading.Thread(target=tryNotify, args=('zzz',))
    t.start()
    # tryNotify()
    print('結束')
    return 'ok'




if __name__ == '__main__':
    res = startTesting()
    print('res:'+res)