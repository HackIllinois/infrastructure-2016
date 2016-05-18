# HackIllinois Infrastructure 2016

The repository for all core HackIllinois infrastructure used for the 2016 hackathon is stored here.

## Notices

* This codebase currently holds both front-end and back-end components, although this is not how we expect things to be maintained in the future.
* The code stored here needs to be refactored before it can be re-used. As such, we will only be accepting changes for refactors of existing code (as opposed to changes that include new features).
* Contributions to this codebase are to be made via dedicated feature/fix/refactor branches, and a pull-request should be opened into `staging` to request a merge upstream (except in rare circumstances, i.e. hotfixes). All pull-requests should be code-reviewed before being accepted.

## Setup

#### Overview
HackIllinois 2016 is a Google App Engine project written in Python. The specific Python version that is used in production is Python 2.7.x, and we recommend using version 2.7.10 or 2.7.11.

In general, we use the `webapp2` framework to handle requests and responses while using the `ndb` datastore for data persistence.

External libraries for Python such as `requests` are not included directly in this codebase, but it is necessary for them to be present in the build process. These types of dependencies will be installed by the same script that spins up your local instances.

#### Installation
In order to set up a development environment on your local machine, do the following:
  1. [Download Python 2.7.x](https://www.python.org/downloads/)
  2. [Download the App Engine SDK](https://cloud.google.com/appengine/downloads?hl=en)
  3. Clone this repository

## Development

#### Local Instance
In order to start developing on your local machine:
  1. Obtain a HackIllinois key file
  2. Set an environment variable called `HACKILLINOIS_KEYFILE` to point to the file above
  3. Run `npm install && gulp dev` to build the front-end components and watch for new changes
  4. Run `sh scripts/run.sh` relative to the root of the project directory to build the back-end components and spin up an App Engine instance

Note that the front-end and back-end compilation steps should be executed in separate processes.

#### Hidden Files and Folders
The build system will create a `.temp` and `.venv` folder the first time you run the build script. The `.temp` directory is intended to store application data. The `.venv` directory is intended to hold a [virtualenv](https://pypi.python.org/pypi/virtualenv) for the project.

## Deployment

#### Authentication
Naturally, we don't let everyone deploy to our App Engine instances. To authenticate yourself,
you will need to let App Engine have an OAuth token. If it cannot find one, it will walk you through the necessary steps to getting one.

#### Release
New releases should almost always have an incremented version number (updated in `generated/app.yaml`) and should be tested on the development server before going live. To deploy to the development server, run `sh scripts/deploy.sh dev`. Likewise, to deploy to production, run `sh scripts/deploy.sh prod`.

The script will ensure that you are on the correct branch before executing the release, so please be sure that you have checked out the required branch and, more importantly, pulled the updated changes.
