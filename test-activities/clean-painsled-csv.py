#!/Users/cfa5228/.pyenv/versions/garmin-export/bin/python

"""
Have set the password and usernname using keyring.set_password(). For the
username, we used the fake username 'garminexport_username' so we could
abuse keyring and store the username as a password.
"""
#%%
from cgi import test
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
from pyprojroot import here
from urllib3 import Retry

#%%
input_dir_path = str(here("test-activities/original-files"))
activity_dir = os.listdir(input_dir_path)
output_dir_path = str(here("test-activities/cleaned-files"))

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

# %%
test_file = dt.fread("xrscrn_20221018T220042261Z.csv")

#%%
def rename_painsled_csv_vars(file_name, input_dir_path):
    file = input_dir_path + "/" + file_name
    DT = dt.fread(file)
    
    DT.names = {
        "ElapsedTime (sec)": "Seconds",
        "Horizontal (meters)" : "Meters",
        "Power (watts)" : "Watts",
        "Cadence (strokes/min)" : "Cadence",
        "HRCur (bpm)" : "Hrate"
    }

    return DT

def feature_painsled_vars(DT):
    DT[:, dt.update(**{
        "Torq (N-m)" : None,
        "s_500m" : ifelse(f.Watts == 0, 0, 500*(2.8/f.Watts)**(1/3)),
        "ID" : 0,
        "Calc_stroke_dist_m" : ifelse( # Takes multiple conditions
            shift(f.Meters) == None, f.Meters,
            f.Meters - shift(f.Meters) < 0, f.Meters,
            f.Meters - shift(f.Meters)
        ),
        "Calc_time_diff_sec": ifelse(
            shift(f["TimeStamp (sec utc)"]) == None,
            f["Seconds"],
            f["TimeStamp (sec utc)"] - shift(f["TimeStamp (sec utc)"])
        )
        })]
        
    DT[:, dt.update(**{
        "m_s" : ifelse(f.Watts == 0, 0, 500/f.s_500m),
        "Cum_dist_m" : f["Calc_stroke_dist_m"].cumsum(),
        "Cum_time_sec" : f["Calc_time_diff_sec"].cumsum()
        })]
    DT[:, dt.update(**{
        "Km/h" : ifelse(f.Watts == 0, 0, f.m_s*3.6),
        "Km" : f.Cum_dist_m/1000,
        "Minutes" : f.Cum_time_sec/60
        })]

    DT = DT[:, ["Minutes", "Torq (N-m)","Km/h","Watts","Km","Cadence","Hrate","ID", "StrokeCount"]]

    return DT


def correct_painsled_lap_num(DT):
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
    
    return DT

def correct_painsled_filename(DT):
    datetime_obj = datetime.fromtimestamp(DT[0, "TimeStamp (sec utc)"])
    filename_str = datetime_obj.strftime("%Y_%m_%d_%H_%M_%S")

    return filename_str

#%%
def clean_painsled_csv(csv_file, input_dir_path, output_dir_path):
    renamed_DT = rename_painsled_csv_vars(csv_file, str(input_dir_path))
    featured_DT = feature_painsled_vars(renamed_DT)
    output_DT = correct_painsled_lap_num(featured_DT)
    filename_str = correct_painsled_filename(renamed_DT)
    filename_path = output_dir_path + "/" + filename_str + ".csv"

    output_DT.to_csv(filename_path)

#%%
for file in activity_dir:
    if file.startswith("xrscrn_") and file.endswith(".csv"):
        test_DT = clean_painsled_csv(file, input_dir_path, output_dir_path)


#%%
# Minutes,Torq (N-m),Km/h,Watts,Km,Cadence,Hrate,ID
test_file.names = {
    "ElapsedTime (sec)": "Seconds",
    "Horizontal (meters)" : "Meters",
    "Power (watts)" : "Watts",
    "Cadence (strokes/min)" : "Cadence",
    "HRCur (bpm)" : "Hrate",
    }

# %%
test_file[:, dt.update(**{
    "Torq (N-m)" : None,
    "s_500m" : ifelse(f.Watts == 0, 0, 500*(2.8/f.Watts)**(1/3)),
    "ID" : 0,
    "Calc_stroke_dist_m" : ifelse( # Takes multiple conditions
        shift(f.Meters) == None, f.Meters,
        f.Meters - shift(f.Meters) <= 0, f.Meters,
        f.Meters - shift(f.Meters)
    ),
    "Calc_time_diff_sec": ifelse(
        shift(f["TimeStamp (sec utc)"]) == None,
        f["Seconds"],
        f["TimeStamp (sec utc)"] - shift(f["TimeStamp (sec utc)"])
    )
    })]
    
test_file[:, dt.update(**{
    "m_s" : ifelse(f.Watts == 0, 0, 500/f.s_500m),
    "Cum_dist_m" : f["Calc_stroke_dist_m"].cumsum(),
    "Cum_time_sec" : f["Calc_time_diff_sec"].cumsum()
    })]
test_file[:, dt.update(**{
    "Km/h" : ifelse(f.Watts == 0, 0, f.m_s*3.6),
    "Km" : f.Cum_dist_m/1000,
    "Minutes" : f.Cum_time_sec/60
    })]

PD = test_file.to_pandas()

# %%
DT = test_file[:, ["Minutes", "Torq (N-m)","Km/h","Watts","Km","Cadence","Hrate","ID", "StrokeCount"]]
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
del DT[:, "StrokeCount"]

# %%
DT.to_csv("2022_10_30_12_00_00.csv")
# %%
