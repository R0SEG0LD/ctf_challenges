#!/bin/bash

#echo "Please Type number of encryption rounds:"

rounds=$2

input=$1

for i in $(seq $rounds); do
	result="/tmp/encrypt_data_$i"
	if [ $i -eq 1 ]; then
		head -30 /dev/urandom | openssl aes-256-ecb -in $input -kfile - -nosalt -p 2>/dev/null > $result
	else
		head -30 $input | openssl aes-256-ecb -in $input -kfile - -nosalt -p 2>/dev/null > $result
		rm $input
	fi
	input=$result
	
done

cat "$input"
