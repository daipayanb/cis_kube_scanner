from flask import Flask, render_template, redirect, request
from bench_api import apply_yaml, delete_apply
import redis
import json
from json2html import *
#from rejson import Client, Path

#rj = Client(host='localhost', port=6379, decode_responses=True)
r = redis.StrictRedis()

app = Flask(__name__)
"""
def get_tests(test_data):
    final_test_dict = {}
    for xdict in test_data:
        test_data = {}
        test_data["section"] = xdict["section"]
        test_data["pass"] = xdict["pass"]
        test_data["fail"] = xdict["fail"]
        test_data["warn"] = xdict["warn"]
        test_data["info"] = xdict["info"]
        test_data["desc"] = xdict["desc"]
        results_dict = {}
        for rdict in xdict["results"]:
            if rdict["status"] != "PASS":
                results_dict[rdict["test_number"]+rdict["status"]] = rdict[""]
"""

def retrieve_data(json_data):
    data_dict = {}
    data_dict["nodename"] = json_data["nodename"]
    data_dict["timestamp"] = json_data["timestamp"]
    data_dict["id"] = json_data["id"]
    data_dict["version"] = json_data["version"]
    data_dict["text"] = json_data["text"]
    data_dict["node_type"] = json_data["node_type"]
    print(data_dict)
    return data_dict, get_tests(json_data["tests"])

def get_tests(tests):
    results_dict = {}
    results_dict["Test Number"] = "Test Description"
    for tdict in tests:
        for rdict in tdict["results"]:
            """
            data = ""
            data += "Status: " + rdict["status"] + " || "
            data += "Test Description: " + rdict["test_desc"] + " || "
            data += "Audit: " + rdict["audit"] + " || "
            data += "AuditConfig: " + rdict["AuditConfig"] + " || "
            data += "Type: " + rdict["type"] + " || "
            data += "Remediation: " + rdict["remediation"] + " || "
            """
            data = []
            data.append("Status: " + rdict["status"])
            data.append("Test Description: " + rdict["test_desc"])
            data.append("Audit: " + rdict["audit"])
            data.append("AuditConfig: " + rdict["AuditConfig"])
            data.append("Type: " + rdict["type"])
            data.append("Remediation: " + rdict["remediation"])
            #print(data)
            results_dict[rdict["test_number"]] = data
            #print(rdict["test_number"])
            #results_dict["test_number"]
    return results_dict


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
def posted():
    data = request.json[0]
    nodename = data['nodename']
    print(nodename)
    #r = redis.Redis(host='localhost', port=6379, db=0)
    r.execute_command('JSON.SET', nodename, '.', json.dumps(data))
    #rj.jsonset(nodename, Path.rootPath(), data)
    print(json.loads(r.execute_command('JSON.GET', nodename)))
    json_node, json_data = retrieve_data(data)
    node_table = json2html.convert(json = json_node)
    test_table = json2html.convert(json = json_data)
    #json2html.convert()
    f = open('templates/results.html','w')
    html_file = "<html><head></head><body><p>" + node_table + '<br>' + test_table + "</p></body></html>"
    f.write(html_file)
    f.close()
    #print(rj.jsonget(nodename))
    #print(json.dumps(request.json[0]))
    #print()
    return "OK"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)