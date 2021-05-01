import execjs
import os
import sys


def apns(tokenID, text, sendName, RoomID, msgID, userID, msgType):
    print('收到並開始通知')
    try:
        ctx = execjs.compile("""
        var fs = require('fs');
        var jwt = require('jsonwebtoken');

        function apns(tokenID, text, sendName, RoomID, msgID, userID, msgType){
            var epochtime = Date.now() / 1000 
            var cert = fs.readFileSync('AuthKey_7Q7CZ5PDJH.p8');  // get private key
            var token = jwt.sign({
                "iss": "CXB28GPWN9",
                "iat": parseInt(epochtime)}, cert, { header: {"alg": "ES256", "kid": "7Q7CZ5PDJH"}, algorithm: 'ES256'});
            console.log(tokenID)

            var apn = require('apn');

            var options = {
            token: {
                key: "AuthKey_7Q7CZ5PDJH.p8",
                keyId: "7Q7CZ5PDJH",
                teamId: "CXB28GPWN9"
            },
            production: false
            };

            var apnProvider = new apn.Provider(options);
            var note = new apn.Notification();
            let deviceToken = tokenID;
            
            note.title = sendName;
            note.body = text;
            note.category = '{"RoomID":"' + RoomID + '", "UserID":"' + userID + '", "MsgID":"' + msgID + '", "MsgType":"' + msgType + '"}';
            note.sound = "default";
            note.badge = 1;
            note.setAction("MEETING_INVITATION").setMutableContent(1);
            note.contentAvailable = 1;	
            note.topic = "com.nkust.flutterMessenger";

            apnProvider.send(note, deviceToken).then( (result) => {
                process.exit();
                // see documentation for an explanation of result
            });
        }
        """)
        ctx.call("apns", tokenID, text, sendName, RoomID, msgID, userID, msgType)
        print('send Notify')
    except:
        print('apns Err:',sys.exc_info()[0])

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    apns(*sys.argv[1:])
