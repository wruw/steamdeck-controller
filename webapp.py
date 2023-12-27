from flask import Flask, render_template
import PyATEMMax

app = Flask(__name__)
cameras = [False, False, False, False, False, False, False, False]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/count')
def count():
    global c
    c += 1
    return str(c)

if __name__ == '__main__':
    app.run()
