if [ "$#" -ne 1 ]; then
	echo "ERROR: Incorrect usage"
	echo "You must supply a target (prod or dev)"
	exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $DIR/helpers.sh

branch=$(cd $DIR/../ && git branch | sed -n -e 's/^\* \(.*\)/\1/p')
if [ "$1" == "prod" ]; then
	if [ "$branch" != "master" ]; then
		echo "ERROR: You are on branch '$branch' but should be on 'master'"
		exit 1
	else
		echo "You are about to deploy to *** production ***"
		if f_confirm "Is this correct?"; then
			echo

			source $DIR/deploy/prod.sh
			f_pre_deploy
			f_deploy
			exit 0
		else
			echo
			echo "Deployment aborted"
			exit 1
		fi
	fi
elif [ "$1" == "dev" ]; then
	if [ "$branch" != "staging" ]; then
		echo "ERROR: You are on branch '$branch' but should be on 'staging'"
		exit 1
	else
		echo "You are about to deploy to *** development ***"
		if f_confirm "Is this correct?"; then
			echo

			source $DIR/deploy/dev.sh
			f_pre_deploy
			f_deploy
			exit 0
		else
			echo
			echo "Deployment aborted"
			exit 1
		fi
	fi
else
	echo "ERROR: Unknown target '$1'"
	echo "Available targets are prod and dev"
fi
