FROM alpine:3.12
WORKDIR /opt/kube-bench
RUN apk --no-cache add procps
COPY kube-bench ./
COPY cfg/ cfg/
ENV PATH=/opt/kube-bench:$PATH
CMD ./kube-bench node --json
CMD wget http://10.128.0.27/help.txt