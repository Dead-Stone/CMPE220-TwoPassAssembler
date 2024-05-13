import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from assembler import assemble

app = Flask(__name__)

UPLOADS_FOLDER = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assemble', methods=['POST'])
def upload_assembly():
    code = request.form.get('code')
    file = request.files.get('file')

    if file and file.filename:
        try:
            # Ensure 'uploads' directory exists
            if not os.path.exists(UPLOADS_FOLDER):
                os.makedirs(UPLOADS_FOLDER)

            file_path = os.path.join(UPLOADS_FOLDER, file.filename)
            file.save(file_path)
            output_path, errors = assemble(file_path)
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    elif code:
        try:
            if not os.path.exists(UPLOADS_FOLDER):
                os.makedirs(UPLOADS_FOLDER)

            file_path = os.path.join(UPLOADS_FOLDER, 'temp_code.asm')
            with open(file_path, 'w') as f:
                f.write(code)
            output_path, errors = assemble(file_path)
            os.remove(file_path)
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    else:
        return redirect(url_for('index'))

    if errors:
        return render_template('index.html', errors=errors)
    else:
        return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
