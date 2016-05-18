DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

sh $DIR/build.sh
if [ $? != 0 ]; then
	exit $?
fi

echo "Creating temporary directory..."
mkdir -p $DIR/../.temp
mkdir -p $DIR/../.temp/storage

echo
echo "Starting development server:"
dev_appserver.py --storage_path=$DIR/../.temp/storage $DIR/../app.yaml

echo
echo "Removing app file..."
rm -rf $DIR/../app.yaml
