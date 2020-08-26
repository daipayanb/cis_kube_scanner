from flask import Flask, render_template, redirect, request
from bench_api import apply_yaml, delete_apply
import redis
import json
from rejson import Client, Path

rj = Client(host='localhost', port=6379, decode_responses=True)
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/button_start', methods = ['POST'])
def start():
    global POD_NAME
    POD_NAME = apply_yaml()
    return redirect("http://localhost:8000/", code=302)



@app.route('/button_end', methods = ['POST'])
def end():
    delete_apply(POD_NAME)
    return redirect("http://localhost:8000/", code=302)

@app.route('/data', methods = ['POST'])
def data():
    data = request.json[0]
    nodename = data['nodename']
    print(nodename)
    #r = redis.Redis(host='localhost', port=6379, db=0)
    rj.jsonset(nodename, Path.rootPath(), data)
    print(rj.jsonget(nodename))
    #print(json.dumps(request.json[0]))
    #print()
    return "OK"
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)