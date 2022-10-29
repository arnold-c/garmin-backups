#!/Users/cfa5228/.pyenv/versions/garmin-export/bin/python

"""
Have set the password and usernname using keyring.set_password(). For the
username, we used the fake username 'garminexport_username' so we could
abuse keyring and store the username as a password.
"""

import keyring
import subprocess

username = keyring.get_password("garminexport", "garminexport_username")
password = keyring.get_password("garminexport", username) 

subprocess.call(["zsh", "import-script.sh", username, password])
