from flask import Flask, request, send_file, render_template, url_for
from rembg import remove
from PIL import Image
import io
import os
from rembg import remove, new_session

# Preload the model at startup
session = new_session("u2net")  # or "u2netp" for smaller model

print("PORT:", os.environ.get("PORT"))

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'static/processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

output_image_path = None

@app.route('/')
def index():
    return render_template('index.html', output_image=output_image_path)

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    global output_image_path
    if 'image' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400
    output_image=None
    input_image = Image.open(file.stream)
    print(input_image)
    try:
        output_image = remove(input_image,session=session)
    except Exception as e:
        print("Error in remove():", e)
        return "Background removal failed", 500
    print(output_image)
    output_image_path = os.path.join(PROCESSED_FOLDER, 'output.png')
    output_image.save(output_image_path, format='PNG')
    print(output_image_path)
    image_url = url_for('static', filename='processed/output.png') if output_image else None
    return render_template('result.html', output_image=image_url)

    

@app.route('/download')
def download():
    if output_image_path:
        return send_file(output_image_path, mimetype='image/png', as_attachment=True, download_name='output.png')
    return "No image available", 400



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # default to 5000 locally
    app.run(host='0.0.0.0', port=port)
    