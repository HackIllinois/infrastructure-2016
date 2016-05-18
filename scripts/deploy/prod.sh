source $DIR/deploy/common.sh
source $DIR/deploy/cron.sh

function f_pre_deploy {
	echo "Running pre-deployment tasks (cron update, index update, etc)..."
	f_npm_install
	f_gulp_build
	f_write_cron

	sh $DIR/build.sh prod
	if [ $? != 0 ]; then
		echo "ERROR: The build script failed to build the app file"
		exit $?
	fi

	appcfg.py update_cron $DIR/.././
	appcfg.py update_indexes $DIR/.././
}

function f_deploy {
	echo "Deploying changes to production instance..."
	appcfg.py update $DIR/../app.yaml
}
