import mqttPub as mqttPush
import subprocess


# mqttPush.sendNotify('217','60','詹祐祈','AAA')
i="1"
RoomID="100"
Topic = 'User_'+i+"/"+RoomID
MsgID=60
SendName="詹祐祈"
Text="台灣有座阿里山"
# mqttPush.sendNotify(Topic,RoomID,MsgID,SendName,Text)
command = "python3 mqttPub.py " +str(Topic)+" "+str(RoomID)+" "+str(MsgID)+" "+str(SendName)+" "+str(Text)
subprocess.Popen(command, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
