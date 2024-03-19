FROM metabrainz/base-image

RUN apt-get update \
    && apt-get install -y --no-install-recommends vsftpd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/vsftpd/empty \
 && mkdir -p /etc/vsftpd \
 && mkdir -p /var/ftp \
 && mv /etc/vsftpd.conf /etc/vsftpd.orig \
 && mkdir /etc/service/vsftpd

#RUN iptables -A INPUT -p tcp -j DROP
#RUN iptables -A INPUT -p udp -j DROP

ADD vsftpd.sh /etc/service/vsftpd/run

VOLUME ["/var/ftp"]

EXPOSE 20-21
EXPOSE 65500-65515


# Docker Build
# sudo docker build .

# Docker Run Command
# sudo docker run -d -p [::]:20-21:20-21 -p [::]:65500-65515:65500-65515 -v ./data:/var/ftp:ro {IMAGE ID}
