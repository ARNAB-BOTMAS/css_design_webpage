from flask import Flask, render_template, request
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

load_dotenv()

cloudinary.config(secure=True)

app = Flask(__name__)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded'
        
        file = request.files['file']
        folder = 'my_photos'  # Change to the desired folder in your Cloudinary account
        
        # Upload the file to Cloudinary
        result = cloudinary.uploader.upload(file, folder=folder)
        
        # Print the upload result
        print(result)
        
        return 'File uploaded successfully'
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
