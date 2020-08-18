FROM alpine:3.12
WORKDIR /opt/kube-bench
RUN apk --no-cache add procps
RUN apk --no-cache add curl
COPY kube-bench ./
COPY cfg/ cfg/
COPY sender.sh sender.sh
ENV PATH=/opt/kube-bench:$PATH
CMD ./sender.sh