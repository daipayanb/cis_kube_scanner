# kube-bench_automation

This is a project that automates all the scans and checks implemented in [aquasecurity/kube-bench](https://github.com/aquasecurity/kube-bench) for all the nodes in a cluster and collects the scan results from all the nodes.

For now, the implementation supports the kube-bench scan for worker nodes only. The project makes use of `DaemonSet` to run the pods in all the nodes of a cluster. The DaemonSet YAML file is [job-node_DaemonSet.yaml](https://github.com/daipayanb/kube-bench_distributed/blob/master/job-node_DaemonSet.yaml) and is based on the original [job-node.yaml](https://github.com/daipayanb/kube-bench_distributed/blob/master/job-node.yaml)

The main script is [bench_api.py](https://github.com/daipayanb/kube-bench_distributed/blob/master/bench_api.py) which uses the [kubernetes-client/python](https://github.com/kubernetes-client/python). Going ahead this is the only script that is going to be further developed.

The [trial_unq.sh](https://github.com/daipayanb/kube-bench_distributed/blob/master/trial_unq.sh) and [trial_unq.py](https://github.com/daipayanb/kube-bench_distributed/blob/master/trial_unq.py) are versions which work with local `kubectl` commands. 
