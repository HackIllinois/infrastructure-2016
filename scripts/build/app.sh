source $HACKILLINOIS_KEYFILE

function f_install_deps {
	echo "Installing dependencies..."

	if [ ! -d $DIR/../.venv ]; then
		virtualenv $DIR/../.venv >/dev/null
	fi

	source $DIR/../.venv/bin/activate

	mkdir -p $DIR/../www/libs

	rm -rf $DIR/../www/libs/*
	pip install --upgrade -r requirements.txt -t $DIR/../www/libs/ >/dev/null
	rm -rf $DIR/../www/libs/*.dist-info

	touch $DIR/../www/libs/__init__.py

	deactivate
}

function f_write_app {
	echo "Writing app file..."
	appfile=$(<$DIR/../generated/app.yaml)

	cat > $DIR/../app.yaml <<-EOF
	### THIS FILE IS AUTO-GENERATED
	### YOU SHOULD MAKE ANY NECESSARY CHANGES IN /generated/app.yaml
	$appfile
	EOF
}

function f_inject_keys {
	echo "Injecting keys into app file..."

	sed -i '' -e "s/{{ ADMIN_ID }}/$ADMIN_ID/g" $DIR/../app.yaml
	sed -i '' -e "s/{{ MAILGUN_SECRET }}/$MAILGUN_SECRET/g" $DIR/../app.yaml
	sed -i '' -e "s/{{ HARDWARE_SECRET }}/$HARDWARE_SECRET/g" $DIR/../app.yaml
}

function f_inject_dev {
	APPLICATION_ID=$DEV_APPLICATION_ID
	sed -i '' -e "s/{{ APPLICATION_ID }}/$APPLICATION_ID/g" $DIR/../app.yaml

	IS_DEVELOPMENT="TRUE"
	sed -i '' -e "s/{{ IS_DEVELOPMENT }}/$IS_DEVELOPMENT/g" $DIR/../app.yaml
}

function f_inject_prod {
	APPLICATION_ID=$PROD_APPLICATION_ID
	sed -i '' -e "s/{{ APPLICATION_ID }}/$APPLICATION_ID/g" $DIR/../app.yaml

	IS_DEVELOPMENT="FALSE"
	sed -i '' -e "s/{{ IS_DEVELOPMENT }}/$IS_DEVELOPMENT/g" $DIR/../app.yaml
}

function f_remove_app {
	echo "Removing app file (if it exists)..."
	rm -f $DIR/../app.yaml
}
