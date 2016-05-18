function f_npm_install {
	# NOTE: we expect to remove this method
	# (and the package manager associated with it)
	# once we split our front-end and back-end codebases

	echo "Installing dependencies via NPM... "
	$(cd $DIR/../ && npm install)
}

function f_gulp_build {
	# NOTE: we expect to remove this method
	# (and the task runner associated with it)
	# once we split our front-end and back-end codebases

	echo "Invoking task runner... "
	$(cd $DIR/../ && gulp build:deploy)
}
