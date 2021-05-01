var fs = require('fs');
var jwt = require('jsonwebtoken');


var epochtime = Date.now() / 1000 
var cert = fs.readFileSync('AuthKey_7Q7CZ5PDJH.p8');  // get private key
var token = jwt.sign({
    "iss": "CXB28GPWN9",
    "iat": parseInt(epochtime)}, cert, { header: {"alg": "ES256", "kid": "7Q7CZ5PDJH"}, algorithm: 'ES256'});

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
let deviceToken = '2af03fbd7c21c6efee1643fec3b29cfc60e24b58d5711fd2ec96644d6231b7ee';

note.title = '朱彥銘';
note.body = '測試用的不用害怕';
note.category = '{"RoomID":"101","UserID":"2","MsgID":"1"}';
note.sound = "default";
note.badge = 1;
note.setAction("MEETING_INVITATION").setMutableContent(1);
note.contentAvailable = 1;
note.topic = "com.nkust.flutterMessenger";

apnProvider.send(note, deviceToken).then( (result) => {
    process.exit();
    // see documentation for an explanation of result
});
