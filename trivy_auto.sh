#!/bin/bash

deployments=$(kubectl get deployments | grep -v NAME | awk -F " " '{print $1}')
echo "$deployments"

rm -rf trivy-results
mkdir trivy-results

for deployment in ${deployments}; do
    image=$(kubectl describe deployment ${deployment} | grep Image: | awk -F " " '{print $2}')
    echo "$image"
    echo $(date) >> trivy-results/$deployment
    echo "Image: ${image}" >> trivy-results/$deployment 
    trivy image ${image} >> trivy-results/$deployment
done