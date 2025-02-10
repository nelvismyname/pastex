import os
import brotli
import hashlib
from flask import Flask, request, render_template, send_file, redirect, url_for
import io

app = Flask(__name__)
PASTE_DIR = "pastes"
ALLOWED_EXTENSIONS = {
    "txt", "log", "csv", "tsv", "json", "xml", "yaml", "yml",
    "md", "rst", "ini", "cfg", "conf", "bat", "sh", "sql",
    "html", "htm", "xhtml", "css", "js"
}

os.makedirs(PASTE_DIR, exist_ok=True)

def compress(text):
    return brotli.compress(text.encode())

def decompress(data):
    return brotli.decompress(data).decode()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash(text):
    compressed = compress(text)
    return hashlib.sha256(compressed).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text', '')

        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if allowed_file(file.filename):
                text = file.read().decode('utf-8')
            else:
                return "File type not allowed.", 404

        if not text.strip():
            return "Content not found", 404

        text_hash = hash(text)
        paste_filename = f"{text_hash[:8]}.txt"
        file_path = os.path.join(PASTE_DIR, paste_filename)

        if os.path.exists(file_path):
            return redirect(url_for('raw_paste', paste_id=text_hash[:8]))
        with open(file_path, 'wb') as f:
            f.write(compress(text))

        return redirect(url_for('raw_paste', paste_id=text_hash[:8]))

    return render_template('index.html')

@app.route('/<paste_id>')
def raw_paste(paste_id):
    file_path = os.path.join(PASTE_DIR, f"{paste_id}.txt")
    if not os.path.exists(file_path):
        return "Paste not found", 404

    with open(file_path, 'rb') as f:
        decompressed_text = decompress(f.read())

    return send_file(io.BytesIO(decompressed_text.encode()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
