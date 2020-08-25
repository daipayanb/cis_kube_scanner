from os import path, mkdir
import yaml
from kubernetes import client, config
from time import sleep

config.load_incluster_config()

with open(path.join(path.dirname(__file__), "job-node_DaemonSet.yaml")) as yaml_file:
        daemon = yaml.safe_load(yaml_file)
        apply_resp = client.AppsV1Api().create_namespaced_daemon_set(body=daemon, namespace="default")
        pods_name = apply_resp.metadata.name
        print("DaemonSet created. Daemon-Set name='%s'" % apply_resp.metadata.name)
        sleep(30)
        client.AppsV1Api().delete_namespaced_daemon_set(name=pods_name, namespace="default")
        
"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-deployment
  labels:
    app: python-kube_bench
spec:
  replicas: 1
  selector:
    matchLabels:
      app: python-kube_bench
  template:
    metadata:
      labels:
        app: python-kube_bench
    spec:
      containers:
      - name: python-cont
        image: daipayan95/python-cont:latest
        command: ["/bin/sh"]
---
apiVersion: v1
kind: Pod
metadata:
  name: python-pod
  labels:
    app: python-kube_bench
spec:
  containers:
  - name: python-cont
    image: daipayan95/python-cont:latest
    #command: ["sleep", "120"]
    
{"fruit": "Apple","size": "Large","color": "Red"}
"""
