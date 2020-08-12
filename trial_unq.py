import os
import random, string
import yaml
import time
import datetime
import shutil

def prepare_yaml():
    #Generate a 16 character string to identify the specific kube-bench scan
    unq = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 16))
    with open("job-node_DaemonSet.yaml.template") as f:
        doc = yaml.load(f, Loader=yaml.FullLoader)
    kube_bench_node_name = "kube-bench-node-" + unq

    #Prepare the final DaemonSet yaml file from the template with the unique kube-bench names
    doc['metadata']['name'] = kube_bench_node_name
    doc['spec']['selector']['matchLabels']['name'] = kube_bench_node_name
    doc['spec']['template']['metadata']['labels']['name'] = kube_bench_node_name
    with open(".job-name_kube-bench-node.yaml","a") as f:
        yaml.dump(doc, f)
    return kube_bench_node_name

def kubectl_exec(cmd):
    #Execute kubectl commands
    stream = os.popen(cmd)
    output = stream.read()
    return output

def kubectl_apply():
    #Kubectl apply the kube-bench DaemonSet .yaml file
    output = kubectl_exec('kubectl apply -f .job-name_kube-bench-node.yaml')
    print("Scan has started!\n")
    print(output)

def get_pods(kube_bench_node_name):
    #Return a list of all the kube-bench pods
    output = kubectl_exec('kubectl get pods --no-headers -o custom-columns=":metadata.name"')
    data = output.split()
    pods = []
    for pod in data:
        if kube_bench_node_name in pod:
            pods.append(pod)
    return pods

def get_node(pod):
    #Get the cluster node in which the pod is running
    output = kubectl_exec('kubectl get pod -o=custom-columns=POD:.metadata.name,NODE:.spec.nodeName --all-namespaces')
    data = output.split("\n")

    for combination in data:
        if pod in combination:
            return combination.split()[1]

def fetch_logs(pod):
    #Fetch logs for the container
    output= kubectl_exec('kubectl logs ' + pod) 
    return output

def write_logs(kube_bench_node_name):
    #Get a list of the kube-bench pods
    pods = get_pods(kube_bench_node_name)

    #Delete oldedr scan files and create new directory
    if os.path.exists('outputs') == True:
        shutil.rmtree('outputs')
    os.mkdir('outputs')

    #Create the output file and write the scan results
    for pod in pods:
        with open("outputs/"+ get_node(pod),"a") as f:
            f.write(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+"\n")
            f.write(fetch_logs(pod))
    print("The scan has completed and the scan results are in the outputs/ directory\n")


def kubectl_delete():
    #Delete the DaemonSet pods
    output = kubectl_exec('kubectl delete -f .job-name_kube-bench-node.yaml')
    print(output)

    #Delete the previously generated .yaml file
    os.remove('.job-name_kube-bench-node.yaml')

def main():
    kube_bench_node_name = prepare_yaml()
    kubectl_apply()
    time.sleep(45)
    write_logs(kube_bench_node_name)
    kubectl_delete()

if __name__ == "__main__":  
    main()