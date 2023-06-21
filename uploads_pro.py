from dotenv import load_dotenv
load_dotenv()

import pathlib
import cloudinary
import cloudinary.api
import cloudinary.uploader

config = cloudinary.config(secure=True)

def upload(filename, folder="my_photos"):
    stem = pathlib.Path(filename).stem
    res = cloudinary.uploader.upload(filename, public_id=stem, folder=folder)
    return res



# res = upload('test.png')
# print(res)
