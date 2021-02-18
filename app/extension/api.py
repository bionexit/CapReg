import time

users = [

    {'name': 'google', 'contact_name': 'Google_name', 'phone': '123456', 'trade_num': 'TM123456', 'password': '1234a', 'postvalue':7890},
    {'name': 'yahoo', 'contact_name': 'Yahoo', 'phone': '456789', 'trade_num': 'TM45678', 'password': '1234','postvalue':4567},
    {'name': 'wanglin', 'contact_name': 'Yahoo', 'phone': '456789', 'trade_num': 'TM45678', 'password': '1234','postvalue':10000},
    {'name': 'mixianmeng', 'contact_name': 'Yahoo', 'phone': '456789', 'trade_num': 'TM45678', 'password': '1234','postvalue':10000},
    {'name': 'wangzong', 'contact_name': '汪雪春', 'phone': '1861234567', 'trade_num': 'TM45678', 'password': '1234',
     'postvalue': 10000}
]

def tradesysauth(username, password):
    _pwd = str(password).strip()
    _username = str(username).strip().lower()
    logined = False

    for user in users:
        if user['name'].strip() == _username and user['password'].strip() == _pwd:
            print(type(user))
            logined = True
            break
    return logined


def tradesysvalue(username):
    # time.sleep(10000)
    _username = str(username).strip().lower()
    valueinfo = []
    for user in users:
        if user['name'].strip().lower() == _username:
            print(type(user))
            logined = True
            valueinfo.append(user)
            break
    return valueinfo

def rowproxy_to_dict(input):
    result = []
    y = {}
    for item in input:
        y = dict(item)
        result.append(y)
    return result