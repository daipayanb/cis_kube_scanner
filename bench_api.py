"""A python script automating kube-bench worker node scans using the Kubernetes\
    Pythcon Client API"""
import shutil
import random
import string
from time import sleep
from os import path, mkdir
import yaml
from kubernetes import client, config

# api = client.CoreV1Api()
# nodes = api.list_node()
def apply_yaml():
    """Kubectl apply the kube-bench DaemonSet .yaml file"""
    config.load_kube_config()
    #Unique identifier for specific kube-bench runs
    unq = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    with open(path.join(path.dirname(__file__), "job-node_DaemonSet.yaml")) as yaml_file:
        #Load the yaml file
        daemon = yaml.safe_load(yaml_file)
        #Editing the load yaml file with the unique names
        kube_bench_node_name = daemon['metadata']['name'] + "-" + unq
        daemon['metadata']['name'] = kube_bench_node_name
        daemon['spec']['selector']['matchLabels']['name'] = kube_bench_node_name
        daemon['spec']['template']['metadata']['labels']['name'] = kube_bench_node_name
        apply_resp = client.AppsV1Api().create_namespaced_daemon_set(body=daemon, \
            namespace="default")
        print("DaemonSet created. Daemon-Set name='%s'" % apply_resp.metadata.name)
        return apply_resp.metadata.name

def delete_apply(pods_name):
    """Delete the kube-bench DaemonSet"""
    client.AppsV1Api().delete_namespaced_daemon_set(name=pods_name, \
        namespace="default")

def delete_old():
    """Delete results of previous scans"""
    if path.exists('outputs'):
        shutil.rmtree('outputs')
    mkdir('outputs')

def write_logs(node_name, logs):
    """Write the ouput logs to files named Node wise"""
    with open("outputs/"+ node_name +".json", "a") as log_file:
        log_file.write(logs)

def node_pod(pod_name):
    """Get Node in which a pod is running"""
    ret = client.CoreV1Api().list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        if pod_name == i.metadata.name:
            return i.spec.node_name
    return pod_name

def get_pod_list(pods_name):
    """Returns a dictionary with keys= Pod names and value= whether logs of pods are available"""
    ret = client.CoreV1Api().list_pod_for_all_namespaces(watch=False)
    pod_log_status = {}
    print(len(ret.items))
    for i in ret.items:
        if pods_name in i.metadata.name:
            pod_log_status[i.metadata.name] = "LogsNotChecked"
    #print(pod_log_status)
    return pod_log_status

def check_logs_ready(pod_log_status, pods_name):
    """Verify if logs are ready to be fetched based on the\
         status of the pods, restarts and contents of the logs."""
    print(pod_log_status)
    retries = 5
    time = 5
    while retries > 0:
        #Flag updated to True if any changes are made to pod_log_status\
        # if not flag stays false and the retry block is exitted.
        update = False
        sleep(time)
        ret = client.CoreV1Api().list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            #print(i.metadata.name)
            if pods_name in i.metadata.name and pod_log_status[i.metadata.name] != "LogsReady":
                try:
                    if i.status.container_statuses[0].state.waiting.reason == 'CrashLoopBackOff'\
                        or i.status.container_statuses[0].state.waiting.reason == 'Completed'\
                            or i.status.container_statuses[0].restart_count >= 1:
                        pod_log_status[i.metadata.name] = "LogsReady"
                        #print(i.metadata.name, i.status, i.status.container_statuses[0].\
                        # state.waiting.reason)
                        update = True
                except:
                    pod_log_status[i.metadata.name] = "LogsNotReady"
                    print(i.metadata.name + " Kube-bench container in unusable state")
                    update = True
        if not update: #If no updates made
            break
        retries -= 1
        time *= 2 #Sleep time before each re-attempt is doubled
    for pods in pod_log_status: #Print the pods which didin't reach a usuable state
        if pod_log_status[pods] != "LogsReady":
            print("Retried 5 times. Logs from POD: %s are still not available. \
                Please check manually" % pods)
    return pod_log_status

def get_logs(pods_name):
    """Fetch logs for the kub-bench pods"""
    node_object = client.CoreV1Api().list_node() #Fetch number of nodes
    node_n = len(node_object.items)
    pod_n = 0
    while pod_n < node_n:
        #Making sure we have all the pod_names for each of the nodes
        pod_log_status = get_pod_list(pods_name)
        pod_n = len(pod_log_status)

    #Get list of the pods for which logs are ready
    pod_log_status = check_logs_ready(pod_log_status, pods_name)

    for pod in pod_log_status:
        #print(pod + " " + pod_log_status[pod])
        if pod_log_status[pod] == "LogsReady":
            logs_response = client.CoreV1Api().read_namespaced_pod_log(\
            name=pod, namespace="default")
            #Write logs to the files
            node_name = node_pod(pod)
            #[**list_node**](CoreV1Api.md#list_node) | **GET** /api/v1/nodes |
            write_logs(node_name, logs_response)

def main():
    """Main Function"""
    pods_name = apply_yaml()
    delete_old()
    get_logs(pods_name)
    sleep(30)
    delete_apply(pods_name)

if __name__ == "__main__":
    main()
