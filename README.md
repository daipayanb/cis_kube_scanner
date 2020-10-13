# CIS Kubernetes Benchmark Scanner v0.1

Our objective is to perform the CIS Benchmark audit of Kubernetes at scale.

This is achieved by using the scans and checks implemented in [aquasecurity/kube-bench](https://github.com/aquasecurity/kube-bench). Currently kube-bench is the best tool for our purpose, if in future we find an open source tool which does it better than Kube-bench the we may shift to it.

For now, the implementation supports the kube-bench scan for worker nodes only. The project makes use of `DaemonSet` to run the worker pods in all the nodes of a cluster. The DaemonSet YAML file is [job-node_DaemonSet.yaml](https://github.com/daipayanb/kube-bench_distributed/blob/master/job-node_DaemonSet.yaml) and is based on the original [job-node.yaml](https://github.com/daipayanb/kube-bench_distributed/blob/master/job-node.yaml)

The main script is [kube_init.sh](https://github.com/daipayanb/kube-bench_automation/blob/master/kube_init.sh) it does the following:
* Create the necessary Kubernetes service to let the Master node and worder nodes communicate. 
* Create a ServiceAccount which is used by the Python application running within the main container to deploy and delete nodes from the cluster. 
* Starts port forwarding for the user to access the control panel via their browser at http://localhost:8000/. 

The destroyer script [kube_destroy.sh](https://github.com/daipayanb/kube-bench_automation/blob/master/kube_destroy.sh) deletes the Service, ServiceAccount and the Master pod `python-cont`.

The main Python application uses the [kubernetes-client/python](https://github.com/kubernetes-client/python). The control panel is developed using [flask](https://flask.palletsprojects.com/en/1.1.x/). The scan resultsbeing in JSON format are stored in Redis using the [ReJson Library](https://oss.redislabs.com/redisjson/). The JSON scan results are then dynamically written into HTML tables using [json2html](https://pypi.org/project/json2html/).

Going ahead this is the only script that is going to be further developed.