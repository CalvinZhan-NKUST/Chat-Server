import time
import bcrypt



# for i in range(5,15):
#     Password='F108118121'
#     start = time.time()
#     salt = bcrypt.gensalt(rounds=i)
#     passwordAdd = bcrypt.hashpw(Password.encode('utf8'), salt)
#     end = time.time()
#     total = str(round(end - start, 4))+'(s)'
#     print('salt:'+str(i)+' time:'+total)

Password=b'F108118121'
passwordAdd=b'$2b$14$GDk/9462tdT8/JOVw4OGcO5TtzsU01znKAO4VSCVCXhxSPYg8MyRm'
start = time.time()
if bcrypt.checkpw(Password, passwordAdd):
    print("match")
else:
    print("does not match")

print(passwordAdd)
end = time.time()
total = str(round(end - start, 4))+'(s)'
print('time:'+total)