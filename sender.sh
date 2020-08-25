#!/bin/sh
#touch /opt/kube-bench/scan.json
#chmod 777 /opt/kube-bench/scan.json
export scan_results=`./kube-bench node --json`
#ls -al
echo "Scan results"
echo $scan_results
echo $MY_NODE_NAME
#echo $scan_results >> scan.json
#cat scan.json
echo "Scan results"
final_result='[{"'$MY_NODE_NAME'":'$scan_results'}]'
echo $final_result
curl -X POST -H "Content-Type: application/json" -d "$final_result" http://kube-bench-service.default.svc.cluster.local:8080/data