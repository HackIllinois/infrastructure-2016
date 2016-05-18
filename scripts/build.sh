if [ -z "$HACKILLINOIS_KEYFILE" ]; then
	echo "ERROR: the \$HACKILLINOIS_KEYFILE variable is not set"
	exit 1
fi
if [ ! -f "$HACKILLINOIS_KEYFILE" ]; then
	echo "ERROR: Keyfile path is invalid"
	exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TARGET=${1:-dev}

source $DIR/helpers.sh
source $DIR/build/app.sh

f_install_deps
f_write_app
f_inject_keys

if [ "$TARGET" == "dev" ]; then
	f_inject_dev
elif [ "$TARGET" == "prod" ]; then
	f_inject_prod
else
	echo "ERROR: Build target ($TARGET) is invalid."
	exit 1
fi

exit 0
