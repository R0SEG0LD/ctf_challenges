FROM ubuntu:24.04

RUN apt update \
	&& apt install -y python3 snort


RUN mkdir -p /var/ragnaroketal

#COPY ./capture.pcap /var/ragnaroketal/capture.pcap
COPY ./files /var/ragnaroketal
	
EXPOSE 42

ENTRYPOINT ["/bin/python3", "/var/ragnaroketal/server.py"]
