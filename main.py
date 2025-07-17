#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
import os
import glob

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB

@app.route('/', methods = ['GET', 'POST'])
def home():
    files = glob.glob('*.pdf')
    for f in files:
        os.remove(f)
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/compress', methods = ['POST'])
def compress():
    if request.method == 'POST':
        global nam
        f = request.files['file_compress']
        compression_level = request.form.get('compression_level', '/screen')
        nam = f.filename.replace(" ", "_")
        with open("name.txt", "w") as text_file:
            text_file.write(nam)
        f.save(nam)
        print(f"Executing in {os.getcwd()}")
        try:
            os.system('gs -h')
        except:
            os.system('sudo apt-get install ghostscript -y')
        finally:
            os.system(f'gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS={compression_level} -dNOPAUSE -dBATCH -sOutputFile={nam}_Compressed.pdf {nam}')
        size_original = os.path.getsize(nam)
        size_compressed = os.path.getsize(f'{nam}_Compressed.pdf')

    return render_template('download.html', previous_size = size_original, compressed_size = size_compressed)

@app.route('/download', methods = ['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        with open("name.txt", "r") as text_file:
            nam = text_file.read()
        file_path = f'{nam}_Compressed.pdf'
        response = send_file(file_path, as_attachment=True)
        # Remove both original and compressed files after sending
        try:
            os.remove(nam)
        except Exception:
            pass
        try:
            os.remove(file_path)
        except Exception:
            pass
        try:
            os.remove("name.txt")
        except Exception:
            pass
        return response

if __name__ == '__main__':
   app.run(debug = True)
