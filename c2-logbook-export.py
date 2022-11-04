import keyring
import requests
import shutil
from datetime import datetime
from pyprojroot import here

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

def download_file(data_endpoint, index, output_dir_path = ".", headers=headers):
    if data_endpoint[index]["stroke_data"] == True:
        workout_id = data_endpoint[index]["id"]
        workout_datetime = datetime.strptime(res_data[0]["date"], "%Y-%m-%d %H:%M:%S")
        workout_date = workout_datetime.strftime("%Y-%m-%d")
        
        file_endpoint = f"{api_root}/api/users/{username}/results/{workout_id}/export/fit"

        local_filename = workout_date + "_" + file_endpoint.split('/')[7] + "." + file_endpoint.split('/')[-1]
        
        output_filename = output_dir_path + "/" + local_filename

        if os.path.isfile(output_filename):
            print(f"{local_filename} already exists, skipping download")
            return

        with requests.get(file_endpoint, stream=True, headers=headers) as r:
            with open(output_filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        return output_filename

for index, value in enumerate(res_data):
    download_file(res_data, index, output_dir_path)