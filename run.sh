#!/bin/zsh
cd ~/Documents/Repos/garmin-backups/

garmin_username=$(python -m keyring get garminexport garminexport_username)
garmin_password=$(python -m keyring get garminexport $garmin_username)

garmin-backup --backup-dir=activities --format=fit $garmin_username --password=$garmin_password

cp ~/Google\ Drive/My\ Drive/Painsled/*.tcx ./painsled-activities/original-files/
cp ~/Google\ Drive/My\ Drive/Painsled/*.csv ./painsled-activities/original-files/
cp ~/Dropbox/Apps/HRV4Training/*.csv ./hrv4training/

python3 clean-painsled-csv.py
python3 c2-logbook-export.py