#!/Users/cfa5228/.pyenv/versions/garmin-export/bin/python

import keyring
import requests
import shutil
import os
from datetime import datetime
from pyprojroot import here
import datatable as dt
from datatable import *

# Make sure this folder exists, or change it to a folder that you would like
# your activities to be saved to
output_dir_path = str(here("ergdata-activities"))

api_root = "https://log.concept2.com"

"""
Have set the password and usernname using keyring.set_password(). For the
username, we used the fake username 'username' so we could
abuse keyring and store the username as a password.
"""
api_token = keyring.get_password("C2 Logbook", "C2_access_token")
username = keyring.get_password("C2 Logbook", "C2_username")
endpoint = f"{api_root}/api/users/{username}/results"

headers = {"Authorization": f"Bearer {api_token}"}

res = requests.get(endpoint, headers = headers)
res_data = res.json()["data"]

def download_file(data_endpoint, index, output_dir_path = ".", format = "fit", headers = headers):
    if data_endpoint[index]["stroke_data"] == True:
        workout_id = data_endpoint[index]["id"]
        workout_datetime_obj = datetime.strptime(res_data[index]["date"], "%Y-%m-%d %H:%M:%S")
        workout_datetime = datetime.strftime(workout_datetime_obj, "%Y_%m_%d_%H_%M_%S")
        
        file_endpoint = f"{api_root}/api/users/{username}/results/{workout_id}/export/{format}"

        local_filename = workout_datetime + "-" + file_endpoint.split('/')[7] + "." + file_endpoint.split('/')[-1]
        
        if format == "csv":
            output_filename = output_dir_path + "/original-csv/" + local_filename
        else:
            output_filename = output_dir_path + "/" + local_filename

        if os.path.isfile(output_filename):
            print(f"{local_filename} already exists, skipping download")
            return

        with requests.get(file_endpoint, stream=True, headers=headers) as r:
            if r.status_code == 200:
                with open(output_filename, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            else:
                print(f"Error downloading {local_filename}: HTTP Status Code {r.status_code}")
                return
        
        print(f"Downloaded activity ID {workout_id}; workout date = {workout_datetime}")
        return output_filename
        

for index, value in enumerate(res_data):
    download_file(res_data, index, output_dir_path, format="fit")
    download_file(res_data, index, output_dir_path, format="csv")

#%%
csv_input_dir_path = str(here("ergdata-activities/original-csv"))
csv_activity_dir = os.listdir(csv_input_dir_path)
csv_output_dir_path = str(here("ergdata-activities"))

#%%
def rename_ergdata_csv_vars(file_name, input_dir_path):
    file = input_dir_path + "/" + file_name
    DT = dt.fread(file)

    DT.names = {
        "Number" : "StrokeCount",
        "Time (seconds)" : "Seconds",
        "Distance (meters)" : "Meters",
        "Pace (seconds)" : "s_500m",
        "Stroke Rate" : "Cadence",
        "Heart Rate" : "Hrate"
    }

    return DT

def feature_ergdata_vars(DT):
    DT[:, dt.update(**{
        "Torq (N-m)" : None,
        "ID" : 0,
        "Calc_stroke_dist_m" : ifelse( # Takes multiple conditions
            shift(f.Meters) == None, f.Meters,
            f.Meters - shift(f.Meters) < 0, f.Meters,
            f.Meters - shift(f.Meters)
        ),
        "Calc_time_diff_sec": ifelse(
            shift(f.Seconds) == None, f.Seconds,
            f.Seconds - shift(f.Seconds) < 0, f.Seconds,
            f.Seconds - shift(f.Seconds)
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

    DT = DT[:, ["Minutes", "Torq (N-m)","Km/h","Watts","Km","Cadence","Hrate","ID", "StrokeCount", "Seconds", "Meters"]]

    return DT

#%%
def correct_ergdata_lap_num(DT):
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

        elif row != 0 and DT[row, "Seconds"] < DT[row-1, "Seconds"] and DT[row, "Meters"] < DT[row-1, "Meters"]:
            DT[row, "ID"] = DT[row-1, "ID"] + 2
            continue
        
        elif row != 0 and DT[row, "StrokeCount"] > 1:
            DT[row, "ID"] = DT[row-1, "ID"]
            continue
        elif row == DT.shape[0] - 1 and DT[row, "StrokeCount"] == 0:
            DT[row, "ID"] = DT[row-1, "ID"] + 1
    

    del DT[:, ["Seconds", "Meters"]]

    return DT

def rename_ergdata_csv_file(csv_file):
    output_filename = csv_file.split('-')[0] + ".csv"

    return output_filename

#%%
def clean_painsled_csv(csv_file, input_dir_path, output_dir_path):
    renamed_DT = rename_ergdata_csv_vars(csv_file, str(input_dir_path))
    featured_DT = feature_ergdata_vars(renamed_DT)
    output_DT = correct_ergdata_lap_num(featured_DT)
    output_filename = rename_ergdata_csv_file(csv_file)
    filename_path = output_dir_path + "/" + output_filename

    output_DT.to_csv(filename_path)

#%%
for file in csv_activity_dir:
    if file.endswith(".csv"):
        clean_painsled_csv(
            file, csv_input_dir_path, csv_output_dir_path
        )
        print("Cleaned " + file)
# %%
