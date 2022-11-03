#%%
import os
import datatable as dt
from pyprojroot import here
from hrvanalysis import remove_outliers, remove_ectopic_beats, interpolate_nan_values, get_time_domain_features
import pandas as pd
from numpy import nan

#%%
input_dir_path = str(here("elite-hrv/original-files"))
activity_dir = os.listdir(input_dir_path)
output_dir_path = str(here("elite-hrv/cleaned-files"))

#%%
def read_elite_hrv_file(file_name, input_dir_path):
    file = input_dir_path + "/" + file_name
    PD = pd.read_csv(file)

    return PD

#%%
def extract_timestamp(file_name):

#%%
def clean_elite_hrv_txt(csv_file, input_dir_path, output_dir_path):
    renamed_DT = read_elite_hrv_file(csv_file, str(input_dir_path))
    # featured_DT = feature_painsled_vars(renamed_DT)
    # output_DT = correct_painsled_lap_num(featured_DT)
    filename_str = extract_timestamp(renamed_DT)
    filename_path = output_dir_path + "/" + filename_str + ".csv"

    output_DT.to_csv(filename_path)

# %%
for file in activity_dir:
    if file.startswith("20") and file.endswith(".txt"):
        test_PD = read_elite_hrv_file(file, input_dir_path)
        test_list = test_PD.values

        # This remove outliers from signal
        rr_intervals_without_outliers = remove_outliers(
            rr_intervals = test_list,  
            low_rri=300,
            high_rri=2000
        )
        # This replace outliers nan values with linear interpolation
        interpolated_rr_intervals = interpolate_nan_values(
            rr_intervals = rr_intervals_without_outliers,
            interpolation_method = "linear"
        )

        # # This remove ectopic beats from signal
        nn_intervals_list = remove_ectopic_beats(
            rr_intervals = interpolated_rr_intervals,
            method = "malik"
        )
        # # This replace ectopic beats nan values with linear interpolation
        interpolated_nn_intervals = interpolate_nan_values(
            rr_intervals = nn_intervals_list
        )

        # # Remove any nan values that the interpolation missed
        removed_nan_values = [x for x in interpolated_nn_intervals if not(pd.isnull(x)) == True]

        time_domain_features = get_time_domain_features(
            removed_nan_values
            )

        print(time_domain_features)
        print("Cleaned " + file)
# %%

# %%
