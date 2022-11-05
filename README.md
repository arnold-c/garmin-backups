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

I am also trying out the new
[ErgData](https://www.concept2.com/service/software/ergdata) app, so have
written a small script to download all activities from the Concept2 Logbook with
stroke data (i.e. recorded using ErgData). The user can choose the file format
to download them in.

I use [poetry](https://github.com/python-poetry/poetry) to manage the python
dependencies, and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
to manage the python virtual environment.

All Garmin files are downloaded using the
[{`garminexport`}](https://github.com/petergardfjall/garminexport) package as
`*.fit` files as they import nicely into GoldenCheetah and I never manually
import activities into Garmin Connect.
## Set Up
#### Packages

You will need to run the following command in the command line to install all
dependencies, and may want to create a virtual environment for this project. I
had issues with the pip version of `{datatable}`, so I installed the development
build from GitHub.

```
pip install pyenv pyenv-virtualenv
pyenv-virtualenv 3.10.4 garmin-backups
pyenv local garmin-backups
poetry install
pip install git+https://github.com/h2oai/datatable
```

#### Concept2 Logbook

If you use ErgData with the Concept2 Logbook and want to download the Concept2
Logbook stroke-by-stroke data, you will need to create an access token. You can
do this by navigating to the [Concept2 Logbook](https://log.concept2.com/) and
following the steps below:

1. Click on the avatar in the top right corner and select "Edit Profile"
2. Select the "Applications" tab
3. Select the "Connect to Concept2 Logbook API" button
4. Save the access token that is generated
   1. See [the Passwords section](#passwords) below to save this token to your
      keychain

Once you have an access token, you will want to create a directory in your
repository that the logbook data will be downloaded to. By default, all files
will be saved to the folder `./ergdata-activities` (which will need to be
created), but this can be changed by updating the variable `output_dir_path` in
[c2-logbook-export.py](c2-logbook-export.py). Sometimes the `*.fit` files are
corrupted so I also download the activities as `*.csv` files. These are saved to
`./ergdata-activities/original-csv` (which will also need to be created prior to
first run), before a cleaning script is run to calculate lap numbers and format
for Golden Cheetah import (see notes about [PowerTap CSV format](#about) for
Painsled activities above).

#### Passwords

I have written a small python helper script that gets called first to download
the Garmin files by accessing my username and password from the keychain.
Initially you will need to set this up using the python commands below.

```python
import keyring

keyring.set_password("garminexport", "garminexport_username", your garmin username)
keyring.set_password("garminexport", your garmin username, your_garmin_password)
keyring.set_password("C2 Logbook", "C2_username", your C2 username)
keyring.set_password("C2 Logbook", "C2_access_token", your C2 Logbook access token)
```

## Use
### Running Everything

To run everything, all you need to do is open a terminal in the base directory
and run

```
zsh run.sh
```

To stop certain scripts from being included, you can comment out the relevant
scripts in [`run.sh`](run.sh).
