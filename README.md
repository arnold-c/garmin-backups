# garmin-backups
## About

This repository contains a script that backups my activities from Garmin Connect
to a local directory. It also copies activities recorded with the Painsled
rowing app to the same directory and then cleans them so they can be imported
into GoldenCheetah. I've had issues with the Painsled TCX files not importing
correctly into GoldenCheetah, so it was easier to clean the CSV exports and
convert them into a format that GC recognizes ([the PowerTap CSV format is the
simplest as all variables are required for a successful
import](https://github.com/GoldenCheetah/GoldenCheetah/blob/master/src/FileIO/CsvRideFile.cpp)).

I use [poetry](https://github.com/python-poetry/poetry) to manage the python
dependencies, and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
to manage the python virtual environment.

All Garmin files are downloaded using the
[{`garminexport`}](https://github.com/petergardfjall/garminexport) package as
`*.fit` files as they import nicely into GoldenCheetah and I never manually
import activities into Garmin Connect.

## Use
### Set Up

I have written a small python helper script that gets called first to download
the Garmin files by accessing my username and password from the keychain.
Initially you will need to set this up using the python commands below.

```python
import keyring

keyring.set_password("garminexport", "garminexport_username", "your_garmin_username")
keyring.set_password("garminexport", "your_garmin_username", "your_garmin_password")
```

You will also need to run the following command in the command line to install
all dependencies, and may want to create a virtual environment for this project.
I had issues with the pip version of `{datatable}`, so I installed the
development build from GitHub.

```
pip install pyenv pyenv-virtualenv
pyenv-virtualenv 3.10.4 garmin-backups
pyenv local garmin-backups
poetry install
pip install git+https://github.com/h2oai/datatable
```

### Running Everything

To run everything, all you need to do is open a terminal in the base directory
and run

```
zsh run.sh
```
