from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    print('testing......')
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'
