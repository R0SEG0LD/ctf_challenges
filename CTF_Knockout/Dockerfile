FROM ubuntu:22.04
RUN apt update \
 && apt install -y python3

RUN mkdir -p /var/knockout

COPY files/flag.txt /var/knockout/flag.txt
COPY files/server.py /var/knockout/server.py

ADD files/* /var/knockout/

EXPOSE 1337/tcp
EXPOSE 10000-20000/udp

ENTRYPOINT ["/bin/python3", "/var/knockout/server.py"]
