#
# python:3.7.9-alpine3.12 with pyyaml and kubernetes client 
#

FROM python:3.7.9-alpine3.12

RUN pip install pyyaml && pip install kubernetes

COPY job-node_DaemonSet.yaml .
COPY bench_api.py .

CMD ["/bin/sh"]
