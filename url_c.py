import hashlib
import random
import string
from datetime import datetime

# Generate a random quote
def generate_quote():
    characters = string.ascii_letters + string.digits
    quote = ''.join(random.choice(characters) for _ in range(10))
    return quote

def generate_hash():
    import datetime
    hash_key = []
    i = 0
    while i<4:        
        characters = string.ascii_letters + string.digits
        secret_key = ''.join(random.choice(characters) for _ in range(10))
        current_time = datetime.datetime.now()
        message = secret_key + str(current_time)
        hasher = hashlib.sha512()
        encoded_message = message.encode('utf-8')
        hasher.update(encoded_message)
        hash_bytes = hasher.digest()
        hash_code = hash_bytes.hex()
        hash_key.append(hash_code)
        i += 1
    url = '/'.join(hash_key)
    return url

def user_hash(value1, value2):
    secret_key = "Developer_user_"
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    data = f"{value1}{value2}{secret_key}{timestamp}".encode('utf-8')
    hash_object = hashlib.sha256(data)
    hash_code = hash_object.hexdigest()
    return hash_code

# print(user_hash('Arnab Mondal', 'Arnab@8016'))