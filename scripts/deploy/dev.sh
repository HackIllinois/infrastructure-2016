source $DIR/deploy/common.sh
source $DIR/deploy/cron.sh

function f_pre_deploy {
	echo "Running pre-deployment tasks (index update)..."

	f_npm_install
	f_gulp_build
	f_remove_cron

	sh $DIR/build.sh dev
	if [ $? != 0 ]; then
		echo "ERROR: The build script failed to build the app file"
		exit $?
	fi

	appcfg.py update_indexes $DIR/.././
}

function f_deploy {
	echo "Deploying changes to development instance..."
	appcfg.py update $DIR/../app.yaml
}
