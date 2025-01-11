FROM debian:latest

# Setup SSHd
RUN apt-get update && apt-get install -y openssh-server

RUN mkdir -p /var/run/sshd
COPY files/sshd_config /etc/ssh/sshd_config

EXPOSE 22

COPY ./home /home

# Loki User Setup
RUN useradd -m -d /home/loki -s /.c2VjcmV0Ymlu/bash -u 6116 loki
#RUN chown -R "loki:loki" /home/loki
RUN echo 'loki:loki' | chpasswd

#RUN mkdir /home/loki/bin
RUN cp -r /usr/lib64 /home/loki/
RUN mkdir -p /home/loki/lib/x86_64-linux-gnu
RUN cp /usr/lib/x86_64-linux-gnu/libtinfo.so.6 /usr/lib/x86_64-linux-gnu/libc.so.6 /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /home/loki/lib/x86_64-linux-gnu/

RUN cp /bin/bash /home/loki/.c2VjcmV0Ymlu/bash

COPY ./loki.auth_keys /home/loki/.ssh/authorized_keys
COPY ./files/fenrir.*.priv /home/loki/.ssh/

COPY ./flag_part1.txt /home/loki/vault/flag.txt

RUN chmod 'o+r' /home/loki/.ssh/*.priv
#RUN chmod 'o-x' /home/loki/bin/bash # Doesn't Allow the user to start any shell.
RUN chmod -R 'a-w' /home/loki/
RUN chown -R 'root:root' /home/loki
RUN chown -R 'loki:loki' /home/loki/.ssh

# Fenrir User Setup
RUN useradd -m -d /home/fenrir -s /bin/bash -u 1337 fenrir
RUN echo 'fenrir:fenrir' | chpasswd
COPY ./fenrir.auth_keys /home/fenrir/.ssh/authorized_keys
COPY ./files/vault.encrypted /home/fenrir/.ssh/vaultkey.encrypted
RUN chown -R "fenrir:fenrir" /home/fenrir

RUN chmod -R "o-r" /var/log # To ensure user cant expose each others IP's.

# Vault User Setup
RUN mkdir /vault
RUN useradd -m -d /vault -s /bin/bash -u 8008 vault
RUN echo 'vault:vault' | chpasswd
COPY ./vault.auth_keys /vault/.ssh/authorized_keys
COPY ./flag_part2.txt /vault/flag.txt
RUN chmod '660' /vault/flag.txt
RUN chown -R "vault:vault" /vault
RUN chmod -R "o-rwx" /vault


#RUN mount --bind --source /bin --target /home/loki/bin


CMD ["/usr/sbin/sshd", "-D"]
