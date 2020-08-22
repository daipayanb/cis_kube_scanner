from flask import Flask, render_template, redirect, request
from bench_api import apply_yaml, delete_apply
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
    print(request.json)
    return request.json
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)