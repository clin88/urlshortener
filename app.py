from flask import Flask, render_template, request, redirect
from redis import from_url
import string
import requests as REQ
import os

app = Flask(__name__)
redis = from_url(os.environ['REDISCLOUD_URL'])

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/", methods=['POST'])
def add_url():
    url = request.form['url']
    try:
        REQ.get(url)
    except REQ.exceptions.MissingSchema, e:
        return render_template('fail.html', error="Invalid URL.")
    except REQ.RequestException, e:
        return render_template('fail.html', error=e.message)

    index = redis.dbsize() - 1
    success = False
    while not success:
        index += 1
        key = base62(index)
        success = redis.setnx(key, url)

    return render_template('success.html', key=key)

@app.route("/<key>", methods=['GET'])
def forward(key=None):
    url = redis.get(key)
    if url:
        return redirect(url)
    else:
        return render_template('index.html')

def base62(n):
    result = []
    while True:
        n, rem = divmod(n, 62)
        if 0 <= rem <= 9:
            result.append(str(rem))
        elif 10 <= rem <= 35:
            result.append(string.ascii_lowercase[rem-10])
        elif 36 <= rem <= 61:
            result.append(string.ascii_uppercase[rem-36])

        if n == 0:
            break

    return "".join(result)
