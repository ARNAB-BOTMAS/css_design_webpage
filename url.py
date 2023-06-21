import hashlib
import datetime
import random
import string

# Generate a random quote
def generate_quote():
    characters = string.ascii_letters + string.digits
    quote = ''.join(random.choice(characters) for _ in range(10))
    return quote

def generate_hash():
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
