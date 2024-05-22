
import os
import subprocess
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'very_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    print("Created upload folder")
else:
    print("Upload folder already exists")

def run_assembler(input_file):
    orig_dir = os.getcwd()
    cpp_dir = os.path.join(orig_dir, 'cpp')
    executable_path = os.path.join(cpp_dir, 'assembler.exe')
    input_path = os.path.join(orig_dir, app.config['UPLOAD_FOLDER'], input_file)
    output_file = input_path.replace('.txt', '_listFile.txt').replace('.asm', '_listFile.txt')

    print(f"Executable path: {executable_path}")
    print(f"Input file path: {input_path}")
    print(f"Expected output file path: {output_file}")

    if not os.path.isfile(executable_path):
        return "Executable not found in its directory.", False

    try:
        os.chdir(cpp_dir)  # Change to the directory where the executable is
        print("Executing subprocess...")
        result = subprocess.run([executable_path, input_path],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Subprocess finished. Return code: {result.returncode}")
        print(f"Subprocess stdout: {result.stdout}")
        print(f"Subprocess stderr: {result.stderr}")

        if result.returncode != 0:
            return result.stderr or "Error executing assembler.", False

        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                output = f.read()
            return output, True
        else:
            return "Output file was not generated.", False
    except Exception as e:
        print(f"Exception occurred: {e}")
        return str(e), False
    finally:
        os.chdir(orig_dir)  # Always change back to the original directory

@app.route('/', methods=['GET', 'POST'])
def index():
    user_input = ""  # Placeholder for the user's text input
    if request.method == 'POST':
        file = request.files.get('file')
        text_input = request.form.get('input')
        
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filename)
            print(f"File saved at: {filepath}")
            output, success = run_assembler(filename)
        elif text_input:
            filename = 'input.txt'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'w') as f:
                f.write(text_input)
            print(f"Text input saved at: {filepath}")
            output, success = run_assembler(filename)
            user_input = text_input
        else:
            flash('No input provided. Please type or upload your assembly code.')
            return redirect(url_for('index'))
        
        if success:
            return render_template('index.html', output=output, user_input=user_input, display=True)
        else:
            flash(output)
            return redirect(url_for('index'))

    return render_template('index.html', display=False)

if __name__ == '__main__':
    app.run(debug=True)
