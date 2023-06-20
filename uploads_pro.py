from dotenv import load_dotenv
load_dotenv()

import pathlib
import cloudinary
import cloudinary.api
import cloudinary.uploader

config = cloudinary.config(secure=True)

def upload(filename, folder="my_photos"):
    # print(filename)
    stem = pathlib.Path(f"data/{filename}").stem
    res = cloudinary.uploader.upload(filename, public_id=stem, folder=folder)
    print(res)
    return res

# res = upload('https://pipedream.com/s.v0/app_1P6hQ8/logo/orig')
# print(res)
