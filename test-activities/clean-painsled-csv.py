#!/Users/cfa5228/.pyenv/versions/garmin-export/bin/python

"""
Have set the password and usernname using keyring.set_password(). For the
username, we used the fake username 'garminexport_username' so we could
abuse keyring and store the username as a password.
"""
#%%
from dataclasses import MISSING
from distutils.log import error
import os
import shutil
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import csv
import datatable as dt
from datatable import *
from numpy import NaN

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

            return f"{year}_{month}_{day}_{hour}_{minute}_{second}.csv"
            # os.rename(file, new_filename)
        else:
            error("Error: filename does not match expected format")


#%%
for file in activity_dir:
    if file.endswith(".csv"):
        rename_painsled_csv(file)

#%%
# Reset directory pointer as file names have changed
activity_dir = os.listdir()

#%%
for file in activity_dir:
    if file.endswith(".csv"):
        DT = dt.fread(file)
        print(DT[:, {"Elapsed Time (sec)": "Time"}])


# xrscrn_20221018T220042261Z.csv
# xrscrn_20221026T221847640Z.csv
# xrscrn_20221027T222030379Z.csv
# %%
test_file = dt.fread("xrscrn_20221026T221847640Z.csv")

#%%
# Minutes,Torq (N-m),Km/h,Watts,Km,Cadence,Hrate,ID
test_file.names = {
    "ElapsedTime (sec)": "Seconds",
    "Horizontal (meters)" : "Meters",
    # "Speed (m/sec)" : "m_s",
    "Power (watts)" : "Watts",
    "Cadence (strokes/min)" : "Cadence",
    "HRCur (bpm)" : "Hrate",
    # "IntervalType" : "ID",
    # "WorkoutIntervalCount" : "ID"
    }
# %%
test_file.names

# %%
test_file[:, dt.update(
    Minutes = f.Seconds/60,
    Torq = None,
    Km = f.Meters/1000,
    # Km_h = f.m_s*3.6
    Km_h = None,
    ID = 0
    )]

# %%
DT = test_file[:, ["Minutes","Torq","Km_h","Watts","Km","Cadence","Hrate","ID", "StrokeCount"]]
# %%
DT.names

# %%
for row in range(0, DT.shape[0]):
    if row == 0 and DT[row, "StrokeCount"] == 1:
        if DT[99, "StrokeCount"] > 98:
            DT[row, "ID"] = 1
        else:
            DT[row, "ID"] = 0
            continue

    elif row == 0 and DT[row, "StrokeCount"] == 0:
        DT[row, "ID"] = 1
        continue

    elif row != 0 and DT[row, "StrokeCount"] == 0:
        DT[row, "ID"] = DT[row-1, "ID"] + 1
        continue
    elif row != 0 and DT[row, "StrokeCount"] == 1:
        DT[row, "ID"] = DT[row-1, "ID"] + 1
        continue
    elif row != 0 and DT[row, "StrokeCount"] > 1:
        DT[row, "ID"] = DT[row-1, "ID"]
        continue
    elif row == len(PD) - 1 and DT[row, "StrokeCount"] == 0:
        DT[row, "ID"] = DT[row-1, "ID"] + 1
# %%
PD = DT.to_pandas()
# %%