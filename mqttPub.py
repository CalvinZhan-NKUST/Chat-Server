import paho.mqtt.client as mqtt
import json
import configparser
import datetime 
import time
import random


config = configparser.ConfigParser()
config.read('config.ini')

def sendNotify(RoomID, MsgID, SendName, Text):
    client = mqtt.Client()
    client.username_pw_set(config['MQTT']['mqtt_account'],config['MQTT']['mqtt_password'])
    client.connect('chatapp.54ucl.com', 1883)
    payload = {'SendName':SendName, 'Text':Text, 'RoomID':RoomID, 'MaxSN':MsgID}
    print (json.dumps(payload, ensure_ascii=False))
    client.publish(str(RoomID), json.dumps(payload, ensure_ascii=False))
    return 'ok'



# # 設置日期時間的格式
# ISOTIMEFORMAT = '%m/%d %H:%M:%S'

# # 連線設定
# # 初始化地端程式
# client = mqtt.Client()

# # 設定登入帳號密碼
# client.username_pw_set(config['MQTT']['mqtt_account'],config['MQTT']['mqtt_password'])

# # 設定連線資訊(IP, Port, 連線時間)
# client.connect(config['MQTT']['mqtt_server_ip'], config['MQTT']['mqtt_port'])

# while True:
#     t0 = random.randint(0,30)
#     t = datetime.datetime.now().strftime(ISOTIMEFORMAT)
#     payload = {'Result' : '我想要畢業'}
#     print (json.dumps(payload, ensure_ascii=False))
#     # 要發布的主題和內容
#     client.publish("217", json.dumps(payload, ensure_ascii=False))
#     time.sleep(2)
