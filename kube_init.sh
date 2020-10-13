#!/bin/bash

#Creates the kube-bench-service service to for the python-cont test-kube and the port-forward
kubectl apply -f service.yaml
sleep 5
#Creates the kubernetes service account to let the scanner deploy and delete nodes 
kubectl apply -f sa_kube_bench.yaml
sleep 5
#Deploys the main Master node which runs the webservice and deploys the worker nodes
kubectl run python-cont --image=daipayan95/python-cont --serviceaccount='sa-kube-bench' --labels='app=python-kube_bench'
sleep 5
#Port-forwarding the port 8080 on the container to localhost:8000
kubectl port-forward svc/kube-bench-service 8000:8080

echo "Check http://localhost:8000/"