import hashlib
import base64
import os

# print(hashlib.sha256(b'test').hexdigest())
# print(hashlib.sha256(b'test').hexdigest())

user_name = 'user1'
user_pass = 'password'
db = {}

# 事前にハッシュ値がわかっている場合の対策
salt = base64.b64encode(os.urandom(32))
print(salt)

# def get_digest(password):
#     password = bytes(password, 'utf-8')
#     digest = hashlib.sha256(salt + password).hexdigest()
#     # さらに暗号化の複数回指定することで対策
#     for _ in range(10000):
#         digest = hashlib.sha256(bytes(digest, 'utf-8')).hexdigest()
#     print(digest)
#     return digest

# get_digestと同様の処理
digest = hashlib.pbkdf2_hmac(
    'sha256', bytes(user_pass, 'utf-8'), salt, 10000
)

# db[user_name] = get_digest(user_pass)

# def is_login(user_name, password):
#     return get_digest(password) == db[user_name]
def is_login(user_name, password):
    digest = hashlib.pbkdf2_hmac(
        'sha256', bytes(password, 'utf-8'), salt, 10000
    ) 
    return digest == db[user_name]

db[user_name] = digest

print(is_login(user_name, user_pass))