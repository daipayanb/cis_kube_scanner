from flask import Flask, render_template, redirect, request, flash
from bench_api import apply_yaml, delete_apply
from time import sleep
from os import urandom
import redis
import json
from json2html import *

r = redis.StrictRedis()

app = Flask(__name__)
app.secret_key = urandom(24)

SCANNING = False
SCAN_COMPLETED = False

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
    global SCANNING
    if SCANNING:
        flash("Scan is already running. Please wait.")
        return redirect("http://localhost:8000/", code=302)
    SCANNING = True
    global POD_NAME
    POD_NAME = apply_yaml()
    global NODE_DICT
    NODE_DICT = {}
    #flash("Scan is now running!")
    #render_template("running.html")
    sleep(60)
    delete_apply(POD_NAME)
    flash("Scan has completed. Check Scan Results")
    #render_template("completed.html")
    sleep(2)
    SCANNING = False
    global SCAN_COMPLETED
    SCAN_COMPLETED = True
    return redirect("http://localhost:8000/", code=302)
    


@app.route('/button_end', methods = ['POST'])
def end():
    global SCAN_COMPLETED
    global SCANNING
    if not SCAN_COMPLETED and not SCANNING :
        flash("No scans running.")
        return redirect("http://localhost:8000/", code=302)
    delete_apply(POD_NAME)
    SCANNING = False
    return redirect("http://localhost:8000/", code=302)

@app.route('/data', methods = ['POST'])
def posted():
    data = request.json[0]
    nodename = data['nodename']
    print(nodename)
    NODE_DICT[nodename] = True
    #r = redis.Redis(host='localhost', port=6379, db=0)
    r.execute_command('JSON.SET', nodename, '.', json.dumps(data))
    return "OK"

def generate_html():
    node_list = NODE_DICT.keys()
    section_html = ""
    for node in node_list:
        json_data = json.loads(r.execute_command('JSON.GET', node))
        node_data, test_data = retrieve_data(json_data)
        node_table = json2html.convert(json = node_data)
        test_table = json2html.convert(json = test_data)
        section_html += node_table + '<br>' + test_table + '<br>'
    header_string = "<h1><center><b> Welcome to kube-bench_automation v0.1! </b></center></h1>"
    scan_string = "<h2><center><b> Scan Results Ready! </b></center></h2><br>"
    html_string = "<html><head>" + header_string + scan_string +"</head><body><p>" + section_html + "</p></body></html>"
    return html_string



@app.route('/show_scans', methods = ['POST'])
def show_scans():
    global SCANNING
    if SCANNING:
        flash("Scan not yet completed. Please wait.")
        return redirect("http://localhost:8000/", code=302)
    
    if not SCAN_COMPLETED:
        flash("No scans have been run yet.")
        return redirect("http://localhost:8000/", code=302)

    for items in NODE_DICT:
        print(items+"\n")
        #print(json.loads(r.execute_command('JSON.GET', items)))
    html_string = generate_html()
    f = open('templates/results.html','w')
    f.write(html_string)
    f.close()
    return render_template("results.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)