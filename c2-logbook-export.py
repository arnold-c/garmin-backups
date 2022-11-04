import keyring
import requests
import shutil
from datetime import datetime
from pyprojroot import here

output_dir_path = str(here("ergdata-activities"))

api_root = "https://log.concept2.com"
api_token = keyring.get_password("C2 Logbook", "access_token")
username = keyring.get_password("C2 Logbook", "username")
endpoint = f"{api_root}/api/users/{username}/results"

headers = {"Authorization": f"Bearer {api_token}"}

res = requests.get(endpoint, headers = headers)
res_data = res.json()["data"]

def download_file(url, workout_date, output_dir_path = "."):
    local_filename = workout_date + "_" + url.split('/')[7] + "." + url.split('/')[-1]
    
    output_filename = output_dir_path + "/" + local_filename

    with requests.get(url, stream=True) as r:
        with open(output_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return output_filename

for index, value in enumerate(res_data):
    if res_data[index]["stroke_data"] == True:
        workout_id = res_data[index]["id"]
        workout_datetime = datetime.strptime(res_data[0]["date"], "%Y-%m-%d %H:%M:%S")
        workout_date = workout_datetime.strftime("%Y-%m-%d")
        file_endpoint = f"{api_root}/api/users/{username}/results/{workout_id}/export/fit"

        download_file(file_endpoint, workout_date, output_dir_path)