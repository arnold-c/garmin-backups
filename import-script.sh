#!/bin/zsh

garmin-backup --backup-dir=activities --format=fit $1 --password=$2

cp ~/Google\ Drive/My\ Drive/Painsled/*.tcx ./activities/
cp ~/Google\ Drive/My\ Drive/Painsled/*.csv ./activities/
