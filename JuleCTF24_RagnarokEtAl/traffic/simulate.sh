#!/bin/bash
set -e

#sudo iptables -t nat -A OUTPUT -d 127.0.1.53 -j DNAT --to-destination 127.0.0.53
DNSSERVER="DNSStubListenerExtra=127.0.1.53"
if ! [ $(grep "$DNSSERVER" /etc/systemd/resolved.conf) ]; then
	echo "DNS server not added to resolved.conf"
	exit 1
fi
SCRIPT_DIR="$( cd -- "$( dirname -- "$0" )" >/dev/null 2>&1 ; pwd -P )"

# Write DNS entries.
DNS_ENTRIES="""
127.1.0.80 jaetteguide.online 76.123.42.19\n
127.1.0.53 yggdrasil.branches 53.255.255.35\n
127.1.0.123 ragnarok.time 123.123.123.123\n
127.1.0.21 river.end 101.0.0.101\n
127.1.5.14 commune.helhiem 255.255.255.255\n
127.1.66.67 horn.communion 43.24.86.251\n
127.1.4.43 hidden.sight 95.23.89.213\n
127.0.0.1 mimisbrynn.local 0.0.0.0
"""

#/etc/hosts
cp /etc/hosts /tmp/hosts.backup
echo -e $DNS_ENTRIES | sudo awk 'BEGIN { print "\n# The following was added for CTF Ragnarok et Al." } {printf("%s\t%s\n",$1,$2)}' >> /etc/hosts

#./user_config/dns_static_mappings
echo -e $DNS_ENTRIES | awk '{ printf("dns_static %s %s\n",$2,$3) }' > $SCRIPT_DIR/user_config/dns_static_mappings
sudo docker-compose up -d --force-recreate
echo "Giving container some time to start."
sleep 10

function dns_lookup () {
	dig $1 @127.1.0.53
	dig $1 @127.0.0.53
}

GLOBAL_NOISE=1
function extra_traffic () {
	if [[ $GLOBAL_NOISE -eq 1 ]]; then
		case $1 in
			"http")
				echo "http støj"
				curl http://jaetteguide.online/real.gif &>/dev/null
				curl http://jaetteguide.online/real.png &>/dev/null
				curl http://jaetteguide.online/real.bmp &>/dev/null
				curl http://jaetteguide.online/real.exe &>/dev/null;;
			"dns")
				echo "dns støj"
				dns_lookup "horn.communion"
				dns_lookup "mimisbrynn.local"
				dns_lookup "yggdrasil.branches"
				dns_lookup "hidden.sight";;
			"syslog")
				echo "syslog støj"
				logger -d -n 127.1.66.67 "Much have happened in recent future." -t storm
				logger -d -n 127.1.66.67 "Too much for humans eyes to feast upon." -t storm
				logger -d -n 127.1.66.67 "So instead we shall distract them from their true goals" -t storm
				logger -d -n 127.1.5.14 "Surtr has interesting points" -t fenrir;;
			"https")
				echo "krypteret støj"
				dns_lookup "hidden.sight"
				curl -k https://hidden.sight/fake.gif &>/dev/null
				curl -k https://hidden.sight/fake.png &>/dev/null
				curl -k https://hidden.sight/fake.exe &>/dev/null;;
		esac
	fi
}

OLD_HOSTNAME=$(hostname)
sudo hostname "Muspelhiem"

echo "Setting Time up"
timedatectl set-ntp 0
sleep 1 # Delay needed for proces to finish earlier
sudo timedatectl set-time "2024-12-24 16:00:00"

# START Capture
sudo rm $SCRIPT_DIR/capture*

echo "Starting network capture."
CAPTURE_CMD="sudo tcpdump -w capture.pcap -U -i lo not host 127.0.0.53"
$CAPTURE_CMD 2>/dev/null &
CAPTURE_PID=$(ps -aux | grep "$CAPTURE_CMD" | awk '$1 == "root" {printf "%s ",$2} END {print ""}')
sleep 2
#
## SIMULATION
#
echo "Beginning Traffic Simulation..."
extra_traffic "dns"
extra_traffic "https"
sleep 7
extra_traffic "syslog"
dns_lookup "jaetteguide.online"
extra_traffic "dns"
sleep 1
curl jaetteguide.online/ragnarok_guide.html
extra_traffic "http"
sleep 3
curl jaetteguide.online/plans.txt
extra_traffic "dns"
sleep 5
extra_traffic "https"
extra_traffic "dns"
dns_lookup "commune.helhiem"
sleep 1
logger -d -n 127.1.5.14 "This how its done right?" -t Surtr
sleep 1
logger -d -n 127.1.5.14 "I'll take silence as a yes." -t Surtr
extra_traffic "http"
sleep 2
logger -d -n 127.1.5.14 "Muspelhiem is prepared, the gods will fall." -t Surtr
sleep 4
extra_traffic "https"
logger -d -n 127.1.5.14 "Look for the river.end to gather the last flag" -t Surtr
sleep 1
extra_traffic "dns"
logger -d -n 127.1.5.14 "Marching to war, now we are." -t Surtr
# Something something
sleep 5
dns_lookup "river.end"
sleep 1
extra_traffic "https"
ftp  -np ftp://river.end -o /tmp <<EOF
quote USER surtr
quote PASS TheAesirWillFall
binary
rstatus
EOF
sleep 3
extra_traffic "syslog"
extra_traffic "dns"
extra_traffic "http"
sleep 1

#
## CLEANUP
#
echo "Beginning Cleanup."
timedatectl set-ntp 1

sudo hostname $OLD_HOSTNAME

sudo cp /tmp/hosts.backup /etc/hosts

echo "Doing final touchups on network capture."
sleep 5
kill $CAPTURE_PID

NAT_REWRITE_STR=$(echo -e $DNS_ENTRIES | awk '{printf "%s:%s,",$1,$3} END {print ""}' | sed 's/,$//')
tcprewrite -i capture.pcap -o capture_modified.pcap -N "$NAT_REWRITE_STR"
wireshark capture_modified.pcap
