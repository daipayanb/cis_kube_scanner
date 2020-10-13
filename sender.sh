#!/bin/sh
#touch /opt/kube-bench/scan.json
#chmod 777 /opt/kube-bench/scan.json
export scan_results=`./kube-bench node --json`
export timestamp=`date -R`
#ls -al
echo "Scan results"
echo $scan_results
echo $MY_NODE_NAME
#echo $scan_results >> scan.json
#cat scan.json
echo "Scan results"
#final_result='[{"'$MY_NODE_NAME'":'$scan_results'}]'
final_result='[{"nodename":"'$MY_NODE_NAME'","timestamp":"'$timestamp'",'${scan_results:2}
echo $final_result
curl -X POST -H "Content-Type: application/json" -d "$final_result" http://kube-bench-service.default.svc.cluster.local:8080/data