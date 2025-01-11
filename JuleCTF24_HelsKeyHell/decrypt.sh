#!/usr/bin/bash


input=$1

while [ $(grep -P "^key=" $input --binary-files=text) ]
do
	result="/tmp/decrypted_data"
	data="/tmp/data_block"
	key="$(head -n 1 $input | grep -oP "^key=\K.++$" --binary-files=text)"
	tail -n+2 $input > $data
	openssl aes-256-ecb -d -in $data -K $key -nosalt 2>/dev/null > $result
	input=$result
done

cat $input
