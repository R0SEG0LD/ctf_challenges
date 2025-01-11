#!/bin/bash
if [[ $EUID -ne 0 ]]; then
	echo "This script must be run as root"
	exit 1
fi
# To Do:
# Add check for whether stored on "/var/folder" to aviod Nordiske Værksted issue.

SCRIPT_DIR="$( cd -- "$( dirname -- "$0" )" >/dev/null 2>&1 ; pwd -P )"

docker stop ragnarok-container
docker rm ragnarok-container
docker rmi ragnarok-image

docker build -t ragnarok-image $SCRIPT_DIR/.
docker run --name ragnarok-container -d -p 42:1337 ragnarok-image

echo "# Container logs:"
docker logs -f ragnarok-container

