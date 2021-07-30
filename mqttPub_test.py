import paho.mqtt.client as mqtt
import json
import configparser
import datetime 
import time
import random
import os
import sys



# mqttPush.sendNotify('217','60','詹祐祈','AAA')
# i="1"
# RoomID="100"
# Topic = 'User_'+i+"/"+RoomID
# MsgID=60
# SendName="詹祐祈"
# Text="台灣有座阿里山"
# # mqttPush.sendNotify(Topic,RoomID,MsgID,SendName,Text)
# command = "python3 mqttPub.py " +str(Topic)+" "+str(RoomID)+" "+str(MsgID)+" "+str(SendName)+" "+str(Text)
# subprocess.Popen(command, shell=True, bufsize = -1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
config = configparser.ConfigParser()
config.read('config.ini')

Topic='User_1/101'
client = mqtt.Client()
client.tls_set()
client.username_pw_set(config['MQTT']['mqtt_account'],config['MQTT']['mqtt_password'])
client.connect('chatapp.54ucl.com', 1883)
payload = {'SendName':'SendName', 'Text':'Text', 'RoomID':'RoomID', 'MsgID':'MsgID', 'UserID':'userID', 'MsgType':'msgType'}
sendPayload = json.dumps(payload, ensure_ascii=False)
print(sendPayload)
client.publish(str(Topic), sendPayload)


# dataObj = {'UserID':'1', 'uuid':'0000'}
# r = requests.post("http://localhost:4001/keepLogin", data=dataObj)
# print(r.text)
