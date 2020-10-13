"""CIS Kubernetes Benchmark Scanner"""
import json
from os import urandom,system
from time import sleep

from json2html import *
import redis
from flask import Flask, flash, redirect, render_template, request, send_file

from bench_api import apply_yaml, delete_apply

#start a daemonized redis-server with the rejson module
system('redis-server --daemonize yes --loadmodule ./rejson.so')
#Initiate Redis Connection
r = redis.StrictRedis()

#Initiate flask
app = Flask(__name__)
#Templates should be reloaded if there have been new changes made
app.config['TEMPLATES_AUTO_RELOAD'] = True
#A secret required by the Flask.flash() message flashing
app.secret_key = urandom(24)

#Variable to indicate whether a scan is currently in progress
SCANNING = False

#Variable indicating whether a scan has successfully completed
SCAN_COMPLETED = False

def retrieve_data(json_data):
    """Creates a dictionary by parsing the JSON Data. This function only\
        generates the basic node scan data and then calls get_data() for\
        the actual test results data"""
    data_dict = {}
    data_dict["nodename"] = json_data["nodename"]
    data_dict["timestamp"] = json_data["timestamp"]
    data_dict["id"] = json_data["id"]
    data_dict["version"] = json_data["version"]
    data_dict["text"] = json_data["text"]
    data_dict["node_type"] = json_data["node_type"]
    print(data_dict)
    #Returns two dictionaries, one consists of the basic scan details
    #and one containing actual test results
    return data_dict, get_tests(json_data["tests"])

def get_data(tests, status, results_dict):
    """Parses the JSON Test data and creates a Dictionary """
    #There may be multiple test sections. Such as id=4 == Worker Node
    #4.1 and 4.2 test sections
    for tdict in tests:
        #This loop goes test by test within a Test section
        #And its based on the test STATUS, first its the test which have FAIL
        #then WARN and then PASS
        for rdict in tdict["results"]:
            if rdict["status"] == status:
                data = []
                data.append("Status: " + rdict["status"])
                data.append("Test Description: " + rdict["test_desc"])
                data.append("Audit: " + rdict["audit"])
                data.append("AuditConfig: " + rdict["AuditConfig"])
                data.append("Type: " + rdict["type"])
                data.append("Remediation: " + rdict["remediation"])
                results_dict[rdict["test_number"]] = data
    return results_dict

def get_tests(tests):
    """Creates a dictionary of the test results sorted by the STATUS\
        FAIL > WARN > PASS"""
    results_dict = {}
    results_dict["Test Number"] = "Test Description\n"
    results_dict = get_data(tests, "FAIL", results_dict)
    results_dict = get_data(tests, "WARN", results_dict)
    results_dict = get_data(tests, "PASS", results_dict)
    return results_dict


@app.route('/')
def index():
    """Renders index.html"""
    return render_template("index.html")


@app.route('/button_start', methods=['POST'])
def start():
    """On event of clicking Start Scan button"""
    global SCANNING
    #Makes sure that there isn't already an active scan running
    if SCANNING:
        flash("Scan is already running. Please wait.")
        return redirect("http://localhost:8000/", code=302)
    SCANNING = True
    global POD_NAME
    #Using bench_api.py's apply_yaml() the DaemonSet is aplied
    #via Kube Server API
    POD_NAME = apply_yaml()
    #NODE_DICT stores the NODE_NAMEs
    global NODE_DICT
    NODE_DICT = {}
    #Waiting for the scan to complete
    sleep(60)
    #After 60 seconds the using bench_api.py's delete_apply() will
    #delete the DaemonSet
    delete_apply(POD_NAME)
    flash("Scan has completed. Check Scan Results")
    sleep(2)
    #Indicate that the scan has completed and no active scans in progress
    SCANNING = False
    #Indicate that the scan has completed successfully
    global SCAN_COMPLETED
    SCAN_COMPLETED = True
    return redirect("http://localhost:8000/", code=302)


@app.route('/button_end', methods=['POST'])
def end():
    """On event of clicking the END button. This will immediately delete the
     running active scan."""
    global SCAN_COMPLETED
    global SCANNING
    #Making sure that there is an actually running active scan
    if not SCAN_COMPLETED and not SCANNING:
        flash("No scans running.")
        return redirect("http://localhost:8000/", code=302)
    #Using bench_api.py's delete_apply() will delete the DaemonSet
    delete_apply(POD_NAME)
    #Indicate no active scans running
    SCANNING = False
    return redirect("http://localhost:8000/", code=302)

@app.route('/data', methods=['POST'])
def posted():
    """The worker nodes' wrapper script post the scan results to this path"""
    data = request.json[0]
    nodename = data['nodename']
    print(nodename)
    #Indicate that the data for this nodename has been received
    NODE_DICT[nodename] = True
    #Store the JSON scan data in Redis with nodename as the object name
    r.execute_command('JSON.SET', nodename, '.', json.dumps(data))
    return "OK"


def generate_html():
    """Responsible for generating the entire results.html string"""
    global NODE_DICT
    #List of nodes
    node_list = NODE_DICT.keys()
    section_html = ""
    section_links = "<h3>Following Nodes were scanned: </h3><br>"
    for node in node_list:
        #Fetch JSON data for object=NodeName from Redis
        json_data = json.loads(r.execute_command('JSON.GET', node))
        #Get dictionaries parsed from the JSON Data
        node_data, test_data = retrieve_data(json_data)
        #Convert the basic scan data to an HTML Table
        node_table = json2html.convert(json=node_data)
        #Convert the complete Test scan data to an HTML Table
        test_table = json2html.convert(json=test_data)
        #Links to the sections of scan results for each node
        section_links += '<a href="#' + node + '">' + node + '</a><br>'
        node_sections = '<p id="' + node + '">' + "Test results for: " + node + '</p><br>'
        #HTML Tables for each node
        section_html += node_sections + node_table + '\n<br>' + test_table + '<br>'
    header_string = "<h1><center><b> \
        Welcome to CIS Kubernetes Benchmark Scanner v0.1! </b></center></h1>"
    scan_string = "<h2><center><b> Scan Results Ready! </b></center></h2><br>"
    #Concatenating all the parts into the final HTML String
    html_string = "<html><head>" + header_string + scan_string + section_links + \
        "</head><body><div style=\"width:960px;word-wrap: break-word;\"><p>" + section_html + "</p></div></body></html>"
    return html_string


def color_code():
    """Color code the rows of the test results as per PASS/WARN/FAIL"""
    results_file = open('templates/results.html', 'r')
    new_html_string = ""
    for line in results_file:
        if "PASS" in line:
            print(line.replace("<td>","<td style=\"background-color:#00FF00\">"))
            new_html_string += line.replace("<td>","<td style=\"background-color:#00FF00\">")
        elif "FAIL" in line:
            print(line.replace("<td>","<td style=\"background-color:#FF4500\">"))
            new_html_string += line.replace("<td>","<td style=\"background-color:#FF4500\">")
        elif "WARN" in line:
            print(line.replace("<td>","<td style=\"background-color:#FFFF00\">"))
            new_html_string += line.replace("<td>","<td style=\"background-color:#FFFF00\">")
        else:
            new_html_string += line
    return new_html_string

@app.route('/show_scans', methods=['POST'])
def show_scans():
    """On event of clicking the Show Scans button"""
    global SCANNING
    #Checks that there are no active scans
    if SCANNING:
        flash("Scan not yet completed. Please wait.")
        return redirect("http://localhost:8000/", code=302)
    #Checks that a scan has actually completed
    if not SCAN_COMPLETED:
        flash("No scans have been run yet.")
        return redirect("http://localhost:8000/", code=302)
    """
    for items in NODE_DICT:
        print(items+"\n")
        #print(json.loads(r.execute_command('JSON.GET', items)))
    """
    #Fetch the HTML string that needs to be written to the results.html template
    html_string = generate_html()
    results_file = open('templates/results.html', 'w')
    results_file.write(html_string)
    results_file.close()
    new_html_string = color_code()
    results_file = open('templates/new_results.html', 'w')
    results_file.write(new_html_string)
    results_file.close()
    #from_file('templates/results.html','results.pdf')
    return render_template("new_results.html")

"""
@app.route('/download', methods=['POST'])
def download_file():
    path = "templates/results.pdf"
    return send_file(path, as_attachment=True)
"""

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
