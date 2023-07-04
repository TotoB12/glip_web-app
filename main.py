from flask import Flask, render_template, request, send_from_directory, session
import os
import replicate
import threading
import time

app = Flask(__name__)
app.secret_key = 'super secret key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_image():
    uploaded_file = request.files['file']

    uploaded_file.save("static/" + uploaded_file.filename)

    output = replicate.run(
        "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608",
        input={"image": open("static/" + uploaded_file.filename, "rb")},
        caption=True
    )

    session['image_file'] = uploaded_file.filename

    t = threading.Thread(target=delete_file, args=(uploaded_file.filename,))
    t.start()

    return render_template('result.html', caption=output, image=uploaded_file.filename)

@app.route('/question', methods=['POST'])
def ask_question():
    uploaded_file = request.files['file']

    uploaded_file.save("static/" + uploaded_file.filename)

    question = request.form['question']

    output = replicate.run(
        "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608",
        input={"image": open("static/" + uploaded_file.filename, "rb"), "question": question}
    )

    session['image_file'] = uploaded_file.filename

    t = threading.Thread(target=delete_file, args=(uploaded_file.filename,))
    t.start()

    return render_template('result.html', answer=output, image=uploaded_file.filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def delete_file(filename):
    time.sleep(10)
    os.remove(os.path.join('static', filename))

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = os.path.basename('uploads')
    app.run(host='0.0.0.0', port=5000, debug=True)