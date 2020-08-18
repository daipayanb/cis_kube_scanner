#!/bin/sh
touch /opt/kube-bench/scan.json
chmod 777 /opt/kube-bench/scan.json
export scan_results=`./kube-bench node --json`
ls -al
echo "Scan results"
echo $scan_results >> scan.json
cat scan.json
echo "Scan results"
curl -X POST -H "Content-Type: application/json" -d "$scan_results" http://104.154.254.6/data