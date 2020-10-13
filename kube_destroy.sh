#!/bin/bash

#Delete the kube-bench-service 
kubectl delete -f service.yaml
sleep 5
#Delete the kubernetes service account
kubectl delete -f sa_kube_bench.yaml
sleep 5
#Delete the main Master node
kubectl delete pod python-cont

echo "Please Ctrl+C out of the kube_nit.sh if it is still running to kill the port-forward process"