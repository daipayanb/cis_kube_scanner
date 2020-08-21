#
# python:3.7.9-alpine3.12 with pyyaml and kubernetes client 
#

FROM python:3.7.9-alpine3.12

RUN pip install pyyaml && pip install kubernetes && pip install flask

COPY job-node_DaemonSet.yaml .
COPY bench_api.py .
COPY kube_flask.py .
COPY /templates /templates

CMD ["/bin/sh"]
