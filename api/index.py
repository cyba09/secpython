from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def home():
    response = requests.get('https://api.my-ip.io/v2/ip.json')
    print(response.text)
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'
