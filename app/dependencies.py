from fastapi.security import OAuth2PasswordBearer
import json

# Load the config file

with open('/code/config.json', 'r') as config_file:
    config = json.load(config_file)

# Token function used for auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
