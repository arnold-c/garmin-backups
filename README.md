# garmin-backups

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

To run everything, all you need to do is open a terminal in the base directory
and run

```
zsh run.sh
```
