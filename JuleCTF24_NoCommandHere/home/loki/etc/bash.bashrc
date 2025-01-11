bind 'set disable-completion on'
case $SHLVL in
	2)
		echo "Think you can escape just like that huh? Think Again." ;;
	3)
		echo "Damn, you thought twice would do more?" ;;
	4|5|6)
		echo "I can do this all day." ;;
	7)
		echo "Gods you are persistent, you're seriously not getting any commands like this." ;;
	*)
		echo "No more now." 
		exit ;;
esac

source /.bashrc
