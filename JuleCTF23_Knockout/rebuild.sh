#!/bin/bash
sudo docker stop knockout-container
sudo docker rm knockout-container
sudo docker rmi knockout-image

sudo docker build -t knockout-image .
sudo docker run --name knockout-container -d --net=host knockout-image --difficulty 10 --timeout 1 --port 1337
