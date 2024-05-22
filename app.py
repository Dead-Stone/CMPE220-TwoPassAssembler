import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, flash, redirect, url_for

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'very_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Setup logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
                    datefmt='%Y-%m-%d %H:%M:%S')
file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.info('Application startup')

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    app.logger.info("Created upload folder")
else:
    app.logger.info("Upload folder already exists")

def run_assembler(input_file):
    orig_dir = os.getcwd()
    cpp_dir = os.path.join(orig_dir, 'cpp_files')
    executable_path = os.path.join(cpp_dir, 'assembler.exe')
    input_path = os.path.join(orig_dir, app.config['UPLOAD_FOLDER'], input_file)
    output_file = os.path.join(cpp_dir, 'listFile.txt')

    app.logger.info(f"Executable path: {executable_path}")
    app.logger.info(f"Input file path: {input_path}")
    app.logger.info(f"Expected output file path: {output_file}")

    if not os.path.isfile(executable_path):
        app.logger.error("Executable not found in its directory.")
        return "Executable not found in its directory.", False

    try:
        os.chdir(cpp_dir)
        app.logger.info("Executing subprocess...")
        result = subprocess.run([executable_path, input_path],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        app.logger.info(f"Subprocess finished. Return code: {result.returncode}")
        app.logger.debug(f"Subprocess stdout: {result.stdout}")
        app.logger.error(f"Subprocess stderr: {result.stderr}")

        if result.returncode != 0:
            return result.stderr or "Error executing assembler.", False
        app.logger.debug(f'File existence check: {os.path.exists(output_file)}')
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                output = f.read()
            app.logger.debug(output)
            return output, True
        else:
            return "Output file was not generated.", False
    except Exception as e:
        app.logger.exception("Exception occurred")
        return str(e), False
    finally:
        os.chdir(orig_dir)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and (file.filename.endswith('.txt') or file.filename.endswith('.asm')):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            app.logger.info(f"File saved at: {filepath}")
            output, success = run_assembler(file.filename)
            if success:
                return render_template('index.html', output=output, display=True)
            else:
                flash(output)
                return redirect(url_for('index'))
        else:
            flash('Invalid file type or no file uploaded. Please upload a .txt or .asm file.')
            return redirect(url_for('index'))

    return render_template('index.html', display=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
