#!/Users/cfa5228/.pyenv/versions/garmin-export/bin/python

"""
Have set the password and usernname using keyring.set_password(). For the
username, we used the fake username 'garminexport_username' so we could
abuse keyring and store the username as a password.
"""
#%%
import os
from datetime import datetime
import datatable as dt
from datatable import *
from pyprojroot import here

#%%
input_dir_path = str(here("painsled-activities/original-files"))
activity_dir = os.listdir(input_dir_path)
output_dir_path = str(here("painsled-activities/cleaned-files"))

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
        elif row == DT.shape[0] - 1 and DT[row, "StrokeCount"] == 0:
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
        clean_painsled_csv(file, input_dir_path, output_dir_path)
        print("Cleaned " + file)
