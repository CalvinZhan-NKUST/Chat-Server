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
        client.username_pw_set(config['MQTT']['mqtt_account'],config['MQTT']['mqtt_password'])
        client.connect('chatapp.54ucl.com', 1883)
        payload = {'SendName':SendName, 'Text':Text, 'RoomID':RoomID, 'MsgID':MsgID, 'Category':'Message', 'UserID':userID, 'MsgType':msgType}
        print (json.dumps(payload, ensure_ascii=False))
        client.publish(str(Topic), json.dumps(payload, ensure_ascii=False))
        return 'ok'
    elif NotifiType=='NewRoom':
        client = mqtt.Client()
        client.username_pw_set(config['MQTT']['mqtt_account'],config['MQTT']['mqtt_password'])
        client.connect('chatapp.54ucl.com', 1883)
        payload = {'SendName':SendName, 'Text':Text, 'RoomID':RoomID, 'Category':'NewRoom'}
        print (json.dumps(payload, ensure_ascii=False))
        client.publish(str(Topic), json.dumps(payload, ensure_ascii=False))
        return 'ok'

if __name__ == '__main__':
    sendNotify(*sys.argv[1:])