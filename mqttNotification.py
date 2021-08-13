import paho.mqtt.client as mqtt
import json
import configparser
import datetime 
import time
import random
import os
import sys


config = configparser.ConfigParser()
config.read('config.ini')

def sendNotify(Topic, RoomID, MsgID, SendName, Text, NotifiType, userID, msgType):
    if NotifiType=='Message':
        client = mqtt.Client()
        client.tls_set()
        client.username_pw_set(config['MQTT']['mqtt_account'],config['MQTT']['mqtt_password'])
        client.connect('chatapp.54ucl.com', 1883)
        payload = {'SendName':SendName, 'Text':Text, 'RoomID':RoomID, 'MsgID':MsgID, 'UserID':userID, 'MsgType':msgType}
        sendPayload = json.dumps(payload, ensure_ascii=False)
        print(sendPayload)
        client.publish(str(Topic), sendPayload,1)
        return 'ok'
    elif NotifiType=='NewRoom':
        client = mqtt.Client()
        client.tls_set()
        client.username_pw_set(config['MQTT']['mqtt_account'],config['MQTT']['mqtt_password'])
        client.connect('chatapp.54ucl.com', 1883)
        payload = {'SendName':SendName, 'Text':Text, 'RoomID':RoomID, 'MsgID':MsgID, 'MsgType':NotifiType, 'UserID':userID}
        print (json.dumps(payload, ensure_ascii=False))
        client.publish(str(Topic), json.dumps(payload, ensure_ascii=False),1)
        return 'ok'

if __name__ == '__main__':
    sendNotify(*sys.argv[1:])
