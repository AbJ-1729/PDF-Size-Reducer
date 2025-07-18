#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file, session
import os
import glob

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB
app.secret_key = os.environ.get("APP_SECRET_KEY", "3cdf7233c51cda311a79cd1310840c07d28e32805a0177441daeb8c588fa2464")
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
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if request.method == 'POST':
        f = request.files['file_compress']
        # Server-side PDF validation
        if not f.filename.lower().endswith('.pdf') or f.mimetype != 'application/pdf':
            return render_template('index.html', error="Please upload a valid PDF file.")
        compression_level = request.form.get('compression_level', '/screen')
        nam = f.filename.replace(" ", "_")
        session['filename'] = nam  # Changed: Store in session instead of name.txt
        f.save(nam)
        print(f"Executing in {os.getcwd()}")
        try:
            os.system('/usr/bin/gs -h')
        except:
            os.system('sudo apt-get install ghostscript -y')
        finally:
            os.system(f'/usr/bin/gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS={compression_level} -dNOPAUSE -dBATCH -sOutputFile={nam[:-4]}_Compressed.pdf {nam}')
        size_original = os.path.getsize(nam)
        size_compressed = os.path.getsize(os.path.join(BASE_DIR, f'{nam[:-4]}_Compressed.pdf'))

    return render_template('download.html', previous_size = size_original, compressed_size = size_compressed)

@app.route('/download', methods = ['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        nam = session.get('filename')  # Changed: Get from session instead of reading name.txt
        if not nam:
            return redirect(url_for('home'))
        file_path = os.path.join(BASE_DIR, f'{nam[:-4]}_Compressed.pdf')
        response = send_file(file_path, as_attachment=True)
        # Remove both original and compressed files after sending
        try:
            os.remove(os.path.join(BASE_DIR, nam))
        except Exception:
            pass
        try:
            os.remove(file_path)
        except Exception:
            pass
        session.pop('filename', None)  # Changed: Clear from session instead of deleting name.txt
        return response

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)
