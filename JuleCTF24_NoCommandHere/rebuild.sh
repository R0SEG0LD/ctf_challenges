#!/bin/bash
#set -e

# Cleanup
sudo docker stop nocommands-container
sudo docker rm nocommands-container
sudo docker rmi nocommands-image

if [ -f "./*.auth_keys" ]; then
	echo "ERROR: Not auth_keys already exists"
	exit 1
fi

# Prepare key files
cat ./master.pub ./files/fenrir.*.pub > ./fenrir.auth_keys
cat ./master.pub ./files/loki.pub > ./loki.auth_keys
cat ./master.pub ./files/vault.pub > ./vault.auth_keys


sudo docker build -t nocommands-image .
sudo docker run --name nocommands-container -d -p 2222:22 --read-only nocommands-image

rm ./fenrir.auth_keys
rm ./loki.auth_keys
rm ./vault.auth_keys

echo "# Container logs:"
sudo docker logs nocommands-container
