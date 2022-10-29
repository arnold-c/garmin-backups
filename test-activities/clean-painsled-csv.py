#!/Users/cfa5228/.pyenv/versions/garmin-export/bin/python

"""
Have set the password and usernname using keyring.set_password(). For the
username, we used the fake username 'garminexport_username' so we could
abuse keyring and store the username as a password.
"""
#%%
from distutils.log import error
import os
import shutil
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import csv

#%%
activity_dir = os.listdir()

#%%
def rename_painsled_csv(file):

    if file.startswith("xrscrn_"):
        shutil.copy(file, "original-files")
        filename = os.path.basename(file)[7:22]
        if filename[8] == "T":
            dtobj_utc = datetime.strptime(filename, "%Y%m%dT%H%M%S")
            dtobj_utc = dtobj_utc.replace(tzinfo=timezone.utc)
            dtobj_uses = dtobj_utc.astimezone(ZoneInfo("US/Eastern"))

            year = dtobj_uses.year
            month = dtobj_uses.month
            day = dtobj_uses.day
            hour = dtobj_uses.hour
            minute = dtobj_uses.minute
            second = dtobj_uses.second

            new_filename = f"{year}_{month}_{day}_{hour}_{minute}_{second}.csv"
            os.rename(file, new_filename)
        else:
            skip
            error("Error: filename does not match expected format")


#%%
for file in activity_dir:
    if file.endswith(".csv"):
        rename_painsled_csv(file)

#%%
# Reset directory pointer as file names have changed
activity_dir = os.listdir()

# %%
for file in activity_dir:
    if file.endswith(".csv"):
        with open(file, "r") as f:
             print("Rows Counted {} in the csv {}:".format(len(f.readlines()) - 1, file))

# %%
