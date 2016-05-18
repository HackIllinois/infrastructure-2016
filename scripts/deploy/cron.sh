function f_write_cron {
	echo "Writing cron file..."
	cronfile=$(<$DIR/../generated/cron.yaml)

	cat > $DIR/../cron.yaml <<-EOF
	### THIS FILE IS AUTO-GENERATED
	### YOU SHOULD MAKE ANY NECESSARY CHANGES IN /generated/cron.yaml
	$cronfile
	EOF
}

function f_remove_cron {
	echo "Removing cron file (if it exists)..."
	rm -f $DIR/../cron.yaml
}
