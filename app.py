from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_input = None
    output = None
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.endswith('.txt'):
                user_input = file.read().decode('utf-8')  # Assuming file is in UTF-8
                print(1)
                output = "This is the output after processing the file"  # Placeholder for output
            elif 'input' in request.form:
                user_input = request.form['input']
                print(user_input)
                output = "This is the output after processing the text"  # Placeholder for output

        return render_template('index.html', user_input=user_input, output=output, display=True)

    return render_template('index.html', display=False)

if __name__ == '__main__':
    app.run(debug=True)
