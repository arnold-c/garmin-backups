#!/bin/zsh

garmin-backup --backup-dir=activities --format=fit $1 --password=$2

cp ~/Google\ Drive/My\ Drive/Painsled/*.tcx ./painsled-activities/original-files/
cp ~/Google\ Drive/My\ Drive/Painsled/*.csv ./painsled-activities/original-files/

python3 clean-painsled-csv.py
