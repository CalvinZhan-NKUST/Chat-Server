import time
import bcrypt
from datetime import datetime,timezone,timedelta



# for i in range(5,15):
#     Password='F108118121'
#     start = time.time()
#     salt = bcrypt.gensalt(rounds=i)
#     passwordAdd = bcrypt.hashpw(Password.encode('utf8'), salt)
#     end = time.time()
#     total = str(round(end - start, 4))+'(s)'
#     print('salt:'+str(i)+' time:'+total)

# Password=b'F108118121'
# passwordAdd=b'$2b$14$GDk/9462tdT8/JOVw4OGcO5TtzsU01znKAO4VSCVCXhxSPYg8MyRm'
# start = time.time()
# if bcrypt.checkpw(Password, passwordAdd):
#     print("match")
# else:
#     print("does not match")

# print(passwordAdd)
# end = time.time()
# total = str(round(end - start, 4))+'(s)'
# print('time:'+total)

def compare_time(time_1, time_2):
    if time_1 and time_2:
        time_stamp_1 = time.mktime(time.strptime(time_1, '%Y-%m-%d %H:%M'))
        time_stamp_2 = time.mktime(time.strptime(time_2, '%Y-%m-%d %H:%M'))
        if int(time_stamp_1) > int(time_stamp_2):
            return time_2
        else:
            return time_1
    else:
        return None

def get_formattime_from_timestamp(time_stamp):
    date_array = datetime.fromtimestamp(time_stamp)
    time_str = date_array.strftime("%Y-%m-%d %H:%M:%S")
    return time_str


if __name__ == '__main__':
    format_pattern = "%Y-%m-%d %H:%M:%S"

    ts = int(round(time.time() * 1000))
    print(ts)

    # now = time.time()
    # print(now)
    # now02 = time.strftime(format_pattern,time.localtime(now/1000))
    res = get_formattime_from_timestamp(ts/1000)
    print(res)

    # t1 = time.time()
    # print(t1)
    time.sleep(3)

    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))
    t2 = str(dt2.strftime(format_pattern))
    print(t2)

    


    setTime = '2021-05-08 06:35:23'

    difference = (datetime.strptime(t2, format_pattern) - datetime.strptime(setTime, format_pattern))
    # 可以獲取天(days), 或者秒(seconds)
    print(difference)
    print(difference.seconds)
    print(difference.days)
